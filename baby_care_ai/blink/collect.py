# %%
import asyncio
import os
import logging
import datetime
import re
from aiohttp import ClientSession
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file in the repo root
load_dotenv()

config_json_path = os.getenv("CONFIG_JSON_PATH")
output_folder = os.getenv("OUTPUT_FOLDER")

assert config_json_path is not None, (
    "CONFIG_JSON_PATH environment variable must be set."
)
assert output_folder is not None, "OUTPUT_FOLDER environment variable must be set."


async def collect(camera_names: list[str] = None):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    blink = Blink()
    if os.path.exists(config_json_path):
        auth = Auth(await json_load(config_json_path))
        blink.auth = auth
    try:
        await blink.start()
    except:  # if blink.auth is invalid or expired  # noqa: E722
        await blink.prompt_2fa()
        await blink.save(config_json_path)

    # if camera_name is None, save all images; otherwise, save image from the specified cameras
    if camera_names is not None:
        logging.info(f"Collecting images from cameras: {camera_names}")
        for name in camera_names:
            camera = blink.cameras[name]
            await camera.snap_picture()
            await blink.refresh()  # Get new information from server
            processed_name = re.sub(r"_+", "_", name.lower().replace(" ", "_"))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            camera_folder = os.path.join(output_folder, processed_name)
            if not os.path.exists(camera_folder):
                os.mkdir(camera_folder)
            await camera.image_to_file(os.path.join(camera_folder, f"{timestamp}.jpg"))
    else:
        # Take pictures from all cameras and save to designated folder
        for name, camera in blink.cameras.items():
            logging.info(f"Collecting image from camera: {name}")
            camera = blink.cameras[name]
            await camera.snap_picture()  # Take a new picture with the camera
            await blink.refresh()  # Get new information from server
            processed_name = re.sub(r"_+", "_", name.lower().replace(" ", "_"))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            camera_folder = os.path.join(output_folder, processed_name)
            if not os.path.exists(camera_folder):
                os.mkdir(camera_folder)
            await camera.image_to_file(os.path.join(camera_folder, f"{timestamp}.jpg"))


def collect_images(camera_names: list[str] = None):
    asyncio.run(collect(camera_names=camera_names))


if __name__ == "__main__":
    collect_images()
