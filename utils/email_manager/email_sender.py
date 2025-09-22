import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import sys
import os

class EmailMsg:
    def __init__(self) -> None:
        self.smtp_user = os.getenv("SMTP_USER") or ""
        self.smtp_passw = os.getenv("SMTP_PASSW") or ""
        self.smtp_alias = os.getenv("SMTP_ALIAS") or ""
        self.smtp_admin_email = os.getenv("SMTP_ADMIN_EMAIL") or ""

        if "" in [self.smtp_user, self.smtp_passw]:
            logging.critical("SMTP_USER or SMTP_PASSW are empty")
            sys.exit(1)

        self.smtp_conn = self.connectToSMTP(smtp_usr=self.smtp_user, smtp_passw=self.smtp_passw)

    def connectToSMTP(self, *, smtp_usr: str, smtp_passw: str) -> smtplib.SMTP:
        try:
            smtp_server_url = os.getenv("SMTP_SERVER_URL") or ""
            smtp_port = os.getenv("SMTP_SERVER_PORT") or 0
            if "" == smtp_server_url or smtp_port == 0:
                logging.error("SMTP_SERVER_URL AND SMTP_SERVER_PORT cannot be empty")
                sys.exit(1)

            context = ssl.create_default_context()

            server = smtplib.SMTP(smtp_server_url, int(smtp_port)) 
            server.starttls(context=context)
            server.login(smtp_usr, smtp_passw)

            return server
        except smtplib.SMTPAuthenticationError:
            logging.critical("SMTP Auth failed")
            sys.exit(1)

    def createMail(self, *, alias: str, to_email: str, body: str, subject: str) -> MIMEMultipart:
        try:
            msg = MIMEMultipart()
            msg['From'] = alias
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))
            return msg
        except Exception as e:
            logging.error(f"Error creating mail message: {e}")
            sys.exit(1)

    def sendMail(self, *, alias: str, to_email: str, body: str, subject: str, server: smtplib.SMTP) -> None:
        try:
            msg = self.createMail(alias=alias, to_email=to_email, body=body, subject=subject)
            server.sendmail(alias, to_email, msg.as_string())
        except Exception as e:
            logging.error(f"Failed sending mail: {e}")
            sys.exit(1)

    def sendAlert(self, proccesed_domains: int, added_domains: int) -> None: # Auxiliar function to made the alert more readable
        body = f"Added {added_domains} new domains and processed {proccesed_domains} domains"
        self.sendMail(alias=self.smtp_alias, to_email=self.smtp_admin_email, body=body, subject="New domains added - Alert from cert_monitor", server=self.smtp_conn) 
