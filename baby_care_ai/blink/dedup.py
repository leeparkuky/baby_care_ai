# this utils.py would clean up near-duplicate image files daily basis
from dotenv import load_dotenv
import os
from PIL import Image
import imagehash
from PIL import Image
import imagehash
import logging

logger = logging.getLogger(__name__)
load_dotenv()
image_dir = os.getenv("OUTPUT_FOLDER")


def find_most_recent_images(image_dir: str) -> dict:
    """
    Find all image files from the most recent date in each subfolder under the specified image directory.

    Args:
        image_dir (str): The path to the directory containing subfolders of images.

    Returns:
        dict: A dictionary with subfolder names as keys and lists of image file paths from the most recent date as values.
    """
    recent_images = {}

    # Iterate through each subfolder in the image directory
    for subfolder_name in os.listdir(image_dir):
        subfolder_path = os.path.join(image_dir, subfolder_name)
        if os.path.isdir(subfolder_path):
            # List all image files in the subfolder
            image_files = [
                f
                for f in os.listdir(subfolder_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))
            ]
            if image_files:
                # Extract dates from filenames (first 8 characters)
                dates = []
                for f in image_files:
                    try:
                        date_str = f[:8]
                        date = int(date_str)
                        dates.append((date, f))
                    except ValueError:
                        continue  # Skip files that don't start with a valid date

                if dates:
                    # Find the most recent date
                    max_date = max(dates, key=lambda x: x[0])[0]
                    # Collect all files with that date
                    recent_files = [
                        os.path.join(subfolder_path, f)
                        for date, f in dates
                        if date == max_date
                    ]
                    recent_images[subfolder_name] = recent_files

    return recent_images


def deduplicate_images(recent_images: dict, logger: logging.Logger = None) -> None:
    """
    Remove near-duplicate images within each subfolder's list of recent images based on their perceptual hashes.

    Args:
        recent_images (dict): A dictionary with subfolder names as keys and lists of image file paths as values.
        logger (logging.Logger): Optional logger for output. Defaults to module logger.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    total_found = 0
    total_removed = 0

    for folder, image_paths in recent_images.items():
        seen_hashes = {}
        to_remove = []
        total_found += len(image_paths)

        for image_path in image_paths:
            # Calculate the hash of the image
            try:
                img = Image.open(image_path)
                img_hash = imagehash.average_hash(img)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                continue

            # Check if the hash has been seen before
            if img_hash in seen_hashes:
                # If it has, mark for removal
                to_remove.append(image_path)
                logger.info(f"Removed near-duplicate image: {image_path}")
            else:
                # If not, add the hash to the dictionary
                seen_hashes[img_hash] = image_path

        # Remove the duplicates from the list and delete the files
        for path in to_remove:
            os.remove(path)
        recent_images[folder] = [path for path in image_paths if path not in to_remove]
        total_removed += len(to_remove)

    total_survived = total_found - total_removed
    logger.info(f"Total images found: {total_found}")
    logger.info(f"Total images removed: {total_removed}")
    logger.info(f"Total images survived: {total_survived}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    recent_images = find_most_recent_images(image_dir)
    deduplicate_images(recent_images)
    for folder, images in recent_images.items():
        logger.info(f"Unique images from latest date in {folder}: {images}")
