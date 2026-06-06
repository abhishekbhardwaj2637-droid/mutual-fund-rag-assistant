import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# Append current working directory to python path for imports
sys.path.append(os.getcwd())

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
LOG_FILE = os.path.join("data", "pipeline.log")

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_job():
    logging.info("=" * 60)
    logging.info("TRIGGERING DAILY INGESTION PIPELINE JOB")
    logging.info("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Run pipeline script as a subprocess to prevent memory leaks 
        # and guard against SystemExit crashes.
        cmd = [sys.executable, os.path.join("ingestion", "run_pipeline.py")]
        logging.info(f"Executing: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding="utf-8",
            cwd=os.getcwd()
        )
        
        # Stream the stdout/stderr in real-time to our logging handlers
        for line in iter(process.stdout.readline, ''):
            logging.info(f"[pipeline] {line.rstrip()}")
            
        process.wait()
        
        duration = datetime.now() - start_time
        logging.info(f"Pipeline subprocess finished with exit code {process.returncode}")
        logging.info(f"Duration: {duration}")
        
        if process.returncode == 0:
            logging.info("Ingestion pipeline completed successfully.")
        else:
            logging.error(f"Ingestion pipeline failed with exit code {process.returncode}")
            
    except Exception as e:
        logging.error(f"Failed to execute pipeline subprocess: {e}", exc_info=True)
    finally:
        logging.info("=" * 60)

def main():
    logging.info("Mutual Fund Ingestion Scheduler initialized.")
    logging.info(f"Log path configured: {os.path.abspath(LOG_FILE)}")
    
    # Run once immediately on startup to guarantee database is current
    logging.info("Executing initial database synchronization...")
    run_job()
    
    # Run every 24 hours (86,400 seconds)
    # Check if a shorter interval is specified in env (for testing)
    interval_env = os.getenv("SCHEDULER_INTERVAL_SECONDS")
    if interval_env:
        try:
            INTERVAL_SECONDS = int(interval_env)
            logging.info(f"Override: Running with test interval of {INTERVAL_SECONDS} seconds.")
        except ValueError:
            INTERVAL_SECONDS = 24 * 60 * 60
    else:
        INTERVAL_SECONDS = 24 * 60 * 60
        
    logging.info(f"Scheduler entering loop. Next job will run in {INTERVAL_SECONDS} seconds (24 hours).")
    
    try:
        while True:
            time.sleep(INTERVAL_SECONDS)
            run_job()
    except KeyboardInterrupt:
        logging.info("Scheduler terminated by user interrupt.")
    except Exception as e:
        logging.critical(f"Scheduler crashed unexpectedly: {e}", exc_info=True)

if __name__ == "__main__":
    main()
