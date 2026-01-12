# Raspberry Pi Camera Integration

This module provides functionality to capture images from Raspberry Pi devices equipped with cameras, integrating seamlessly with the Baby Care AI automation system.

## Overview

The Raspberry Pi camera integration allows you to capture images from one or more Raspberry Pi devices (such as Raspberry Pi Zero W 2) using SSH and the `rpicam-still` command. Images are automatically collected, timestamped, and stored in the designated output folder alongside Blink camera images.

## Prerequisites

### Hardware
- Raspberry Pi device(s) with camera module (e.g., Raspberry Pi Camera Module 3 or similar)
- Network connectivity (WiFi or Ethernet)
- SSH access enabled on the Raspberry Pi

### Software
- Raspberry Pi OS (or compatible OS) with `rpicam-still` installed
- SSH server running on Raspberry Pi
- Python packages: `fabric`, `python-dotenv`

### Raspberry Pi Setup
1. Ensure `rpicam-still` is installed (usually comes with Raspberry Pi OS)
2. Enable SSH on your Raspberry Pi
3. Configure your camera if needed (e.g., for NoIR cameras)
4. Test camera functionality: `rpicam-still -o test.jpg`

## Configuration

Configure your Raspberry Pi devices in the `.env` file using the following format:

```env
# Raspberry Pi Device Configurations
RPI_DEVICE_1_HOST=192.168.1.129
RPI_DEVICE_1_USER_NAME=pi
RPI_DEVICE_1_PASSWORD=your_password
RPI_DEVICE_1_NAME=living_room_camera
RPI_DEVICE_1_IS_NOIR=false
RPI_DEVICE_1_LOCAL_FILE_PATH=/tmp/capture.jpg
RPI_DEVICE_1_RPICAM_CONFIG="--vflip --hflip --sharpness 1.5 --nopreview -t 500"

# Additional devices
RPI_DEVICE_2_HOST=192.168.1.130
RPI_DEVICE_2_USER_NAME=pi
RPI_DEVICE_2_PASSWORD=another_password
RPI_DEVICE_2_NAME=bathroom_camera
RPI_DEVICE_2_IS_NOIR=true
RPI_DEVICE_2_LOCAL_FILE_PATH=/home/pi/capture.jpg
RPI_DEVICE_2_RPICAM_CONFIG="--nopreview -t 500"
```

### Configuration Parameters

- `HOST`: IP address or hostname of the Raspberry Pi
- `USER_NAME`: SSH username (usually 'pi')
- `PASSWORD`: SSH password
- `NAME`: Descriptive name for the camera (used for folder naming)
- `IS_NOIR`: Set to 'true' if using a NoIR camera (adds tuning file for better image quality)
- `LOCAL_FILE_PATH`: Temporary file path on the Raspberry Pi for image storage
- `RPICAM_CONFIG`: Additional command-line options for `rpicam-still`

## Usage

### Standalone Usage

Run the collection script directly:

```bash
cd baby_care_ai/rpi
python collect.py
```

This will capture images from all configured Raspberry Pi devices and save them to the output folder.

### Integrated with Automation

The Raspberry Pi collection is automatically integrated into the main automation loop (`automation_logic.py`). Images are collected every 3 minutes alongside Blink camera images.

### Manual Capture

You can also use `get_image.py` for testing individual devices:

```bash
python get_image.py
```

## File Structure

Images are organized as follows:
```
collected_images/
├── living_room_camera/
│   ├── 20240111_143022.jpg
│   └── 20240111_143322.jpg
└── bathroom_camera/
    ├── 20240111_143022.jpg
    └── 20240111_143322.jpg
```

## Integration with Main System

- Images from Raspberry Pi cameras are stored in the same output folder as Blink images
- They participate in the same deduplication process
- They are synced to Google Drive alongside other images
- Old images are cleaned up based on the same retention policy

## Troubleshooting

### Authentication Issues
- Verify SSH credentials are correct
- Ensure SSH is enabled on the Raspberry Pi
- Test manual SSH connection: `ssh user@host`

### Camera Issues
- Test camera on Raspberry Pi directly: `rpicam-still -o test.jpg`
- Check camera module is properly connected
- For NoIR cameras, ensure `IS_NOIR=true` and the tuning file path is correct

### Network Issues
- Verify Raspberry Pi is reachable on the network
- Check firewall settings
- Ensure consistent IP addresses (consider static IP or DHCP reservations)

### Permission Issues
- Ensure the SSH user has permission to run `rpicam-still`
- Check write permissions for the local file path on the Raspberry Pi

### Logs
Check the automation log for detailed error messages:
```
tail -f automation.log
```

## Performance Considerations

- SSH connections are established for each capture and closed immediately
- Consider network latency when deploying multiple devices
- Adjust capture intervals in `automation_logic.py` if needed
- Monitor Raspberry Pi CPU and memory usage during captures

## Security Notes

- SSH passwords are stored in the `.env` file (ensure this file is not committed to version control)
- Consider using SSH key authentication for better security
- Keep Raspberry Pi OS updated with security patches