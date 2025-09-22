from psycopg2.pool import ThreadedConnectionPool
from concurrent.futures import ThreadPoolExecutor
from utils.email_manager.email_sender import EmailMsg
import psycopg2
import logging
import sys
import os

class DatabaseAdmin:
    def __init__(self, batch_limit=100, min_conn=1, max_conn=20) -> None:
        self.batch = []
        self.thousand_hundreds_domains = 0
        self.batch_limit = batch_limit
        self.pool: ThreadedConnectionPool

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

    def commit(self) -> None:
        conn = self.pool.getconn()
        if not conn.closed:
            conn.commit()
        else:
            logging.error("Connection is None, cannot commit changes.")
            sys.exit(1)

    def add_batch(self, domain) -> None:
        self.batch.append( (domain[2:],) ) 
        logging.info(f"Added new domain on batch: {domain[2:]}")

        if len(self.batch) >= self.batch_limit:
            self.save_domains()
            
        if self.thousand_hundreds_domains >= 100_000:
            with ThreadPoolExecutor(max_workers=1) as executor: # 1 worker is enough for now
                email = EmailMsg()
                executor.submit(email.sendAlert)

    def save_domains(self):
        logging.info("Commiting domains from batch")
        conn = self.pool.getconn()
        cursor = conn.cursor()
        try:
            cursor.executemany(
                "INSERT INTO domains (domain) VALUES (%s) ON CONFLICT (domain) DO NOTHING;",
                self.batch
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

            self.batch = []
