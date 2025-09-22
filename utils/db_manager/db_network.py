from psycopg2.pool import ThreadedConnectionPool
from concurrent.futures import ThreadPoolExecutor
from utils.email_manager.email_sender import EmailMsg
import threading
import psycopg2
import logging
import sys
import os

class DatabaseAdmin:
    def __init__(self, batch_limit=100, email_workers=1, storage_workers=1, min_conn=1, max_conn=10) -> None:
        self.batch = []
        self.thousand_hundreds_domains = 0
        self.batch_limit = batch_limit
        self.batch_lock = threading.Lock() # Lock for threads using batch
        self.pool: ThreadedConnectionPool
        self.email_executor = ThreadPoolExecutor(max_workers=email_workers)
        self.storage_executor = ThreadPoolExecutor(max_workers=storage_workers)

        try:
            self.pool = ThreadedConnectionPool(
                min_conn,
                max_conn,
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT")
            )
            logging.info("Connected to the database")
        except psycopg2.OperationalError as e:
            logging.critical(f"Cannot connect to the database: {e}")
            sys.exit(1)

    def add_batch(self, domain) -> None:
        with self.batch_lock:
            if domain.startswith('*.') and len(domain) > 2:
                self.batch.append( (domain[2:],) )
            else:
                self.batch.append( (domain,) )

            self.thousand_hundreds_domains += 1

            if len(self.batch) >= self.batch_limit:
                logging.info(f"Added {self.batch_limit} domains")
                batch_to_save = self.batch
                self.storage_executor.submit(self.save_domains, batch_to_save)
                self.batch = []

            if self.thousand_hundreds_domains >= 100_000:
                email = EmailMsg()
                self.email_executor.submit(email.sendAlert)
                self.thousand_hundreds_domains = 0

    def save_domains(self, batch_list):
        logging.info("Commiting domains from batch")
        conn = self.pool.getconn()
        cursor = conn.cursor()
        try:
            cursor.executemany(
                "INSERT INTO domains (domain) VALUES (%s) ON CONFLICT (domain) DO NOTHING;",
                batch_list
            )
            logging.info(f"Domains saved in the background.")

            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            logging.error(f"Error saving the domains: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.pool.putconn(conn)
