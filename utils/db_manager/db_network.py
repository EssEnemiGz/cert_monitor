from psycopg2.pool import ThreadedConnectionPool
from concurrent.futures import ThreadPoolExecutor
from utils.email_manager.email_sender import EmailMsg
import threading
import psycopg2
import logging
import sys
import os

class DatabaseAdmin:
    def __init__(self, batch_limit=100, email_workers=1, storage_workers=1, min_conn=1, max_conn=10, email_alert_amount=10_000_000) -> None:
        self.batch = []
        self.domains_counter = 0
        self.batch_limit = batch_limit
        self.batch_lock = threading.Lock()
        self.pool: ThreadedConnectionPool
        self.email_executor = ThreadPoolExecutor(max_workers=email_workers)
        self.storage_executor = ThreadPoolExecutor(max_workers=storage_workers)
        self.email_alert_amount = email_alert_amount

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
            logging.debug("Connected to the database")
        except psycopg2.OperationalError as e:
            logging.critical(f"Cannot connect to the database: {e}")
            sys.exit(1)

    def add_batch(self, domain) -> None:
        with self.batch_lock:
            if domain.startswith('*.') and len(domain) > 2:
                self.batch.append( (domain[2:],) )
            else:
                self.batch.append( (domain,) )

            self.domains_counter += 1

            if len(self.batch) >= self.batch_limit:
                logging.debug(f"Added {self.batch_limit} domains")
                self.storage_executor.submit(self.save_domains, list(self.batch))
                self.batch = []

    def increase_counter(self, inserted_count) -> None:
        logging.debug(f"Domains saved in the background. New domains added: {inserted_count}")
        self.domains_counter += inserted_count

        if self.domains_counter >= self.email_alert_amount:
            email = EmailMsg()
            self.email_executor.submit(email.sendAlert, self.email_alert_amount)
            self.domains_counter = 0

    def save_domains(self, batch_list):
        logging.debug("Commiting domains from batch")
        conn = self.pool.getconn()
        cursor = conn.cursor()
        try:
            cursor.executemany(
                "INSERT INTO domains (domain) VALUES (%s) ON CONFLICT (domain) DO NOTHING;",
                batch_list
            )
            inserted_count = cursor.rowcount
            with self.batch_lock:
                self.increase_counter(inserted_count)
                logging.debug(f"Domains saved in the background.")

            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            logging.error(f"Error saving the domains: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.pool.putconn(conn)
