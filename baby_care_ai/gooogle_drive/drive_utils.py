# %%
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.settings import LoadSettingsFile
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)


def authenticate_drive(logger=logger) -> GoogleDrive:
    """
    Authenticate with Google Drive.
    Uses a persistent token file to allow for silent refreshing of access tokens,
    enabling non-interactive automation for long periods.
    """
    drive_credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
    # This is where we store the user's specific tokens/session
    token_file = os.path.join(
        os.path.dirname(drive_credentials_path), "google_drive_token.json"
    )

    GoogleAuth.DEFAULT_SETTINGS["client_config_file"] = drive_credentials_path

    settings = LoadSettingsFile(drive_credentials_path)
    settings["oauth_scope"] = ["https://www.googleapis.com/auth/drive"]
    settings["client_config_file"] = drive_credentials_path
    settings["save_credentials"] = True
    settings["save_credentials_file"] = token_file
    settings["save_credentials_backend"] = "file"  # Required for PyDrive2 validation
    settings["get_refresh_token"] = True  # Ensure refresh token is requested
    logger.info("Authenticating Google Drive...")
    gauth = GoogleAuth(settings=settings)

    # Try to load existing credentials (tokens) from the token file
    if os.path.exists(token_file):
        logger.info("Loading credentials from token file...")
        gauth.LoadCredentialsFile(token_file)

    if gauth.credentials is None:
        # No valid credentials found, requires manual browser login\
        logger.info("No valid credentials found, performing manual authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Access token expired, try to refresh silently using the refresh token
        try:
            logger.info("Refreshing access token silently...")
            gauth.Refresh()
        except Exception:
            # If refresh fails (e.g., token revoked), fall back to manual login
            logger.info(
                "Access token refresh failed, performing manual authentication..."
            )
            gauth.LocalWebserverAuth()
    else:
        # Tokens are still valid
        logger.info("Credentials are valid, authorizing...")
        gauth.Authorize()

    # Save the updated credentials (including the new access token) to the file
    logger.info("Saving updated credentials to token file...")
    gauth.SaveCredentialsFile(token_file)
    logger.info("Authentication successful!")

    drive = GoogleDrive(gauth)
    return drive


def find_folder_id(
    folder_name: str, drive: GoogleDrive = None, logger: logging.Logger = None
) -> str:
    """
    Find a Google Drive folder by name.

    Args:
        folder_name: The name of the folder to search for.
        drive: An authenticated Google Drive instance.

    Returns:
        str: The folder ID if found, otherwise an empty string.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    logger.info(f"Searching for folder '{folder_name}' in Google Drive...")
    if drive is None:
        drive = authenticate_drive(logger=logger)

    # Query Google Drive for a folder with the specified name
    file_list = drive.ListFile(
        {
            "q": f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        }
    ).GetList()

    if file_list:
        folder_id = file_list[0]["id"]
        logger.info(f"Found folder '{folder_name}' with ID: {folder_id}")
        return folder_id
    else:
        logger.info(f"Folder '{folder_name}' not found.")
        return ""


def upload_files(
    folder_id: str,
    drive: GoogleDrive = None,
    local_folder: str = None,
    subfolder_names: list[str] = None,
    logger: logging.Logger = None,
) -> None:
    """
    Sync local image files to Google Drive, organizing them into subfolders.

    Args:
        drive: An authenticated Google Drive instance.
        folder_id: The ID of the parent folder in Google Drive.
        local_folder: Path to the local folder containing subfolders with images.
        subfolder_names: List of subfolder names to sync.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    if local_folder is None:
        local_folder = os.getenv("OUTPUT_FOLDER")
    if subfolder_names is None:
        subfolder_names = [
            name
            for name in os.listdir(local_folder)
            if os.path.isdir(os.path.join(local_folder, name))
        ]
    assert local_folder is not None, "OUTPUT_FOLDER is not set"
    assert len(subfolder_names) > 0, f"No subfolders found in {local_folder}"

    if drive is None:
        drive = authenticate_drive(logger=logger)

    # Iterate through each subfolder
    for room_name in subfolder_names:
        folder_name = local_folder + f"/{room_name}"

        # Check if subfolder exists in Google Drive
        q = f"'{folder_id}' in parents and title='{room_name}' and mimeType='application/vnd.google-apps.folder'"
        subfolder_list = drive.ListFile({"q": q}).GetList()

        if subfolder_list:
            subfolder_id = subfolder_list[0]["id"]
            logger.info(f"Found existing {room_name} subfolder")
        else:
            # Create the subfolder if it doesn't exist
            subfolder = drive.CreateFile(
                {
                    "title": room_name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [{"id": folder_id}],
                }
            )
            subfolder.Upload()
            subfolder_id = subfolder["id"]
            logger.info(f"Created '{room_name}' subfolder")

        # Get list of files in local folder and existing files in Google Drive
        files = os.listdir(folder_name)
        existing_files = drive.ListFile({"q": f"'{subfolder_id}' in parents"}).GetList()
        existing_titles = {file["title"] for file in existing_files}

        # Upload image files that don't already exist
        for filename in files:
            if filename.lower().endswith((".jpg", ".png", ".jpeg", ".gif", ".bmp")):
                filepath = os.path.join(folder_name, filename)
                if filename not in existing_titles:
                    file_drive = drive.CreateFile(
                        {"title": filename, "parents": [{"id": subfolder_id}]}
                    )
                    file_drive.SetContentFile(filepath)
                    file_drive.Upload()
                    logger.info(f"Uploaded {filename}")
                elif filename in existing_titles:
                    logger.info(f"Skipped {filename} (already exists)")


# %%
def sync_to_google_drive(
    drive: GoogleDrive = None, logger: logging.Logger = None
) -> None:
    """
    Sync local image files to Google Drive.

    Args:
        drive: An authenticated Google Drive instance.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    if drive is None:
        drive = authenticate_drive(logger=logger)
    local_folder = os.getenv("OUTPUT_FOLDER")
    # list the name of all subfolders in the local_folder
    subfolder_names = [
        name
        for name in os.listdir(local_folder)
        if os.path.isdir(os.path.join(local_folder, name))
    ]
    google_drive_folder_name = os.getenv("GOOGLE_DRIVE_PHOTO_FOLDER_NAME")

    assert google_drive_folder_name is not None, (
        "GOOGLE_DRIVE_PHOTO_FOLDER_NAME is not set"
    )
    parent_folder_id = find_folder_id(google_drive_folder_name, drive, logger=logger)
    if parent_folder_id:
        upload_files(
            folder_id=parent_folder_id,
            drive=drive,
            local_folder=local_folder,
            subfolder_names=subfolder_names,
            logger=logger,
        )
    else:
        print(
            f"Parent folder '{google_drive_folder_name}' not found in Google Drive. Cannot upload files."
        )

    return drive


# %%
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_to_google_drive()
