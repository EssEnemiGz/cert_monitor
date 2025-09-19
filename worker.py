from db_manager.db_network import DatabaseAdmin
from dotenv import load_dotenv
import logging
import psycopg2
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

def process_event(message, context):
    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        try:
            conn = DatabaseAdmin()

            if all_domains:
                for domain in all_domains:
                    logging.info(f"Certificate found for: {domain}")
                    conn.save_domain(domain)
                    conn.commit()

        except psycopg2.Error as e:
            logging.error(f"Database error while processing: {e}")

if __name__ == "__main__":
    logging.info("Starting monitor worker...")
    certstream.listen_for_events(process_event, url='wss://certstream.calidog.io/')
