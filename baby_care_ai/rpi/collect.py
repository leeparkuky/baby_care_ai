from fabric import Connection, Group
from dotenv import load_dotenv
import os
import re
from datetime import datetime as dt
import logging

load_dotenv()
output_folder = os.getenv("OUTPUT_FOLDER")


def load_rpi_configs():
    rpi_configs = {}
    for key in os.environ.keys():
        if key.startswith("RPI_DEVICE_"):
            parts = key.split("_")
            device_num = parts[2]
            param = "_".join(parts[3:])
            if device_num not in rpi_configs:
                rpi_configs[device_num] = {}
            rpi_configs[device_num][param] = os.environ[key]
    return rpi_configs


def get_connection(host, user, password, logger=None):
    # set up logger if logger is None
    if logger is None:
        logger = logging.getLogger(__name__)

    conn = Connection(host=host, user=user, connect_kwargs={"password": password})
    logger.info(f"Established connection to {host} as {user}")
    return conn


def get_pi_image(
    conn, name, rpi_local_file_path, rpicam_configs="", is_noir=False, logger=None
):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    # set up logger if logger is None
    if logger is None:
        logger = logging.getLogger(__name__)
    processed_name = re.sub(r"_+", "_", name.lower().replace(" ", "_"))
    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    camera_folder = os.path.join(output_folder, processed_name)
    if not os.path.exists(camera_folder):
        logger.info(f"Creating folder {camera_folder}")
        os.mkdir(camera_folder)
    local_image_path = os.path.join(camera_folder, f"{timestamp}.jpg")
    try:
        if is_noir:
            conn.run(
                f"rpicam-still -o {rpi_local_file_path} --tuning-file /usr/share/libcamera/ipa/rpi/vc4/imx219_noir.json {rpicam_configs}"
            )
        else:
            conn.run(f"rpicam-still -o {rpi_local_file_path} {rpicam_configs}")
        conn.get(rpi_local_file_path, local=local_image_path)
        logger.info(f"Image saved to {local_image_path}")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        conn.close()


def rpi_images(logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
    rpi_configs = load_rpi_configs()
    logger.info(f"Found {len(rpi_configs)} RPi devices")

    for device_num, config in rpi_configs.items():
        host = config.get("HOST")
        logger.info(f"Connecting to RPi device {device_num} at {host}")
        user = config.get("USER_NAME")
        logger.info(f"Using user {user}")
        password = config.get("PASSWORD")
        name = config.get("NAME", f"rpi_device_{device_num}")
        logger.info(f"Using name {name}")
        is_noir = config.get("IS_NOIR", "false").lower() == "true"
        logger.info(f"Using is_noir {is_noir}")
        rpicam_configs = config.get("RPICAM_CONFIG", "")
        logger.info(f"Using rpicam_configs {rpicam_configs}")
        rpi_local_file_path = config.get("LOCAL_FILE_PATH", "/tmp/image.jpg")
        logger.info(f"Using rpi_local_file_path {rpi_local_file_path}")
        conn = get_connection(host, user, password, logger=logger)
        get_pi_image(
            conn,
            name,
            rpi_local_file_path,
            rpicam_configs=rpicam_configs,
            is_noir=is_noir,
            logger=logger,
        )


if __name__ == "__main__":
    # --- Connection Details ---
    # HOST = "192.168.1.129"
    # USER = "lpark"  # Based on your hostname output
    # PASS = "D!ya4rapw"
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    rpi_images(logger=logger)
