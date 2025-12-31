import os

def setup_config():
    """
    Interactively creates a .env file for the Baby Care AI project.
    """
    print("--- Baby Care AI Configuration Setup ---")
    print("This script will help you create your .env file.\n")
    
    config = {}
    
    # Define fields and their descriptions
    fields = [
        ("CONFIG_JSON_PATH", "Path to save/load Blink authentication JSON", "baby_care_ai/credentials/blink_cred.json"),
        ("OUTPUT_FOLDER", "Local folder for collected images", "collected_images"),
        ("GOOGLE_DRIVE_CREDENTIALS_PATH", "Path to Google Drive client secrets JSON", ""),
        ("GOOGLE_DRIVE_PHOTO_FOLDER_NAME", "Google Drive folder name for uploads", "BabyCarePhotos"),
    ]

    for key, desc, default in fields:
        prompt = f"{desc}"
        if default:
            prompt += f" [default: {default}]"
        prompt += ": "
        
        value = input(prompt).strip()
        if not value and default:
            value = default
        config[key] = value

    # Write to .env
    with open('.env', 'w') as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')
    
    print("\n[+] .env file created successfully!")
    
    # Create necessary directories
    cred_dir = os.path.dirname(config['CONFIG_JSON_PATH'])
    if cred_dir and not os.path.exists(cred_dir):
        os.makedirs(cred_dir)
        print(f"[+] Created directory: {cred_dir}")

    if not os.path.exists(config['OUTPUT_FOLDER']):
        os.makedirs(config['OUTPUT_FOLDER'])
        print(f"[+] Created directory: {config['OUTPUT_FOLDER']}")

    print("\nSetup complete. You can now run the automation.")

if __name__ == "__main__":
    setup_config()
