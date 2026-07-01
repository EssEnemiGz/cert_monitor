from utils.db_manager.db_network import DatabaseAdmin
from functools import partial
from dotenv import load_dotenv
import logging
import certstream
import sys

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("development.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def process_event(db, message, context):
    if 'd' in message:
        all_domains = message['d']

        try:
            if all_domains:
                for domain in all_domains:
                    logging.debug(f"Certificate found for: {domain}")
                    domain = domain.strip().lower()
                    db.add_batch(domain)

        except Exception as e:
            logging.error(f"Database error while processing: {e}")

if __name__ == "__main__":
    logging.info("Starting monitor worker...")
    db = DatabaseAdmin(batch_limit=10000)
    process_event_wrapper = partial(process_event, db)
    certstream.listen_for_events(process_event_wrapper, url='ws://127.0.0.1:4000')
