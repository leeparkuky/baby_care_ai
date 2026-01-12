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

    # Raspberry Pi Device Configuration
    print("\n--- Raspberry Pi Camera Configuration ---")
    add_rpi = input("Do you want to configure Raspberry Pi cameras? (y/n) [n]: ").strip().lower()
    
    if add_rpi in ['y', 'yes']:
        device_count = 0
        while True:
            device_count += 1
            print(f"\nConfiguring Raspberry Pi Device {device_count}:")
            
            host = input(f"Host/IP for device {device_count} (leave empty to stop adding devices): ").strip()
            if not host:
                break
                
            user_name = input(f"SSH username for device {device_count} [pi]: ").strip() or "pi"
            password = input(f"SSH password for device {device_count}: ").strip()
            name = input(f"Device name for device {device_count} [rpi_device_{device_count}]: ").strip() or f"rpi_device_{device_count}"
            is_noir = input(f"Is this a NoIR camera? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            local_file_path = input(f"Local file path on RPi for device {device_count} [/tmp/capture.jpg]: ").strip() or "/tmp/capture.jpg"
            rpicam_config = input(f"Additional rpicam-still options for device {device_count} [--nopreview -t 500]: ").strip() or "--nopreview -t 500"
            
            config[f"RPI_DEVICE_{device_count}_HOST"] = host
            config[f"RPI_DEVICE_{device_count}_USER_NAME"] = user_name
            config[f"RPI_DEVICE_{device_count}_PASSWORD"] = password
            config[f"RPI_DEVICE_{device_count}_NAME"] = name
            config[f"RPI_DEVICE_{device_count}_IS_NOIR"] = str(is_noir).lower()
            config[f"RPI_DEVICE_{device_count}_LOCAL_FILE_PATH"] = local_file_path
            config[f"RPI_DEVICE_{device_count}_RPICAM_CONFIG"] = rpicam_config
            
            print(f"Device {device_count} configured successfully.")
    
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
