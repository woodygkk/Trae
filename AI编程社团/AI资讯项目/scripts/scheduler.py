#!/usr/bin/env python3
"""
Scheduler for automated daily news push
"""

import schedule
import time
import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime
import subprocess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'scheduler.log')
    ]
)

logger = logging.getLogger(__name__)


def load_push_config():
    """Load push configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'push.yaml'

    if not config_path.exists():
        logger.error(f"Push config not found: {config_path}")
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def daily_update_and_push():
    """Daily job: update articles and push to channels"""
    logger.info("=== Running Daily Job ===")

    script_path = Path(__file__).parent / 'ai_news.py'

    try:
        # Step 1: Update database
        logger.info("Step 1: Updating articles...")
        result = subprocess.run(
            [sys.executable, str(script_path), 'update'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode != 0:
            logger.error(f"Update failed: {result.stderr}")
            return

        logger.info("Articles updated successfully")

        # Step 2: Push to channels
        logger.info("Step 2: Pushing to channels...")
        result = subprocess.run(
            [sys.executable, str(script_path), 'push'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Push failed: {result.stderr}")
            return

        logger.info("Push completed successfully")
        logger.info("=== Daily Job Complete ===")

    except subprocess.TimeoutExpired:
        logger.error("Job timeout")
    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)


def hourly_update():
    """Hourly job: just update articles without push"""
    logger.info("=== Running Hourly Update ===")

    script_path = Path(__file__).parent / 'ai_news.py'

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), 'update'],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info("Hourly update complete")
        else:
            logger.error(f"Update failed: {result.stderr}")

    except Exception as e:
        logger.error(f"Hourly update failed: {e}", exc_info=True)


def main():
    """Main scheduler loop"""
    logger.info("AI News Scheduler Started")

    # Load push config to get schedule
    push_config = load_push_config()

    if push_config:
        schedule_config = push_config.get('schedule', {})
        daily_time = schedule_config.get('daily_time', '08:00')

        logger.info(f"Daily push scheduled at: {daily_time}")

        # Schedule daily push
        schedule.every().day.at(daily_time).do(daily_update_and_push)
    else:
        logger.warning("No push config found, using default schedule")
        schedule.every().day.at("08:00").do(daily_update_and_push)

    # Schedule hourly updates (without push)
    schedule.every().hour.do(hourly_update)

    logger.info("Scheduler is running. Press Ctrl+C to stop.")

    # Run the schedule loop
    try:
        # Run update immediately on start
        logger.info("Running initial update...")
        hourly_update()

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
