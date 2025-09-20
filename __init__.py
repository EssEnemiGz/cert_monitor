from worker import process_event
import certstream
import logging

logging.info("Starting monitor worker...")
certstream.listen_for_events(process_event, url='wss://certstream.calidog.io/')
