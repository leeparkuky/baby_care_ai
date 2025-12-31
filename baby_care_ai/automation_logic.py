import time
import logging
import os
from baby_care_ai.blink.collect import collect_images
from baby_care_ai.blink.dedup import find_most_recent_images, deduplicate_images
from baby_care_ai.gooogle_drive.drive_utils import (
    sync_to_google_drive,
    authenticate_drive,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("automation.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

COLLECT_INTERVAL = 3 * 60  # 3 minutes
SYNC_INTERVAL = 0.5 * 60  # 30 minutes
IMAGE_DIR = os.getenv("OUTPUT_FOLDER")


def main():
    last_sync_time = 0

    logger.info("Starting Baby Care AI Automation...")
    logger.info(f"Collection interval: {COLLECT_INTERVAL}s")
    logger.info(f"Sync interval: {SYNC_INTERVAL}s")
    driver = authenticate_drive()
    while True:
        current_time = time.time()

        # 1. Collect images
        logger.info("Step 1: Collecting images from Blink cameras...")
        try:
            collect_images()
            logger.info("Collection successful.")
        except Exception as e:
            logger.error(f"Error during collection: {e}", exc_info=True)

        # 2. Every 1 hour, dedup and sync
        if current_time - last_sync_time >= SYNC_INTERVAL:
            logger.info("Step 2: Starting hourly maintenance (Dedup & Sync)...")
            try:
                # Deduplicate
                logger.info("Running deduplication...")
                recent_images = find_most_recent_images(IMAGE_DIR)
                deduplicate_images(recent_images, logger=logger)

                # Sync to Google Drive
                logger.info("Syncing to Google Drive...")
                driver = sync_to_google_drive(drive=driver, logger=logger)

                last_sync_time = current_time
                logger.info("Hourly maintenance complete.")
            except Exception as e:
                logger.error(f"Error during maintenance: {e}", exc_info=True)

        # Calculate time to wait until next collection
        elapsed = time.time() - current_time
        sleep_time = max(0, COLLECT_INTERVAL - elapsed)

        logger.info(f"Waiting {sleep_time:.1f}s for next cycle...")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
