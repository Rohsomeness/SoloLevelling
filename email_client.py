# flake8: E501 - allow longer lines
"""Scrape email account to find texts that were sent"""
import os

import csv
import email
from email.header import decode_header
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


EMAIL_CSV = "emails.csv"
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"


class EmailClient:
    """Scrape emails from email account"""

    def connect_to_email(self) -> imaplib.IMAP4_SSL:
        """
        Connect to the gmail account using IMAP.

        Returns:
            imaplib.IMAP4_SSL: The connection object for the IMAP server.
        """
        email_username = os.getenv("EMAIL_USERNAME")
        email_password = os.getenv("EMAIL_PASSWORD")

        if not email_username or not email_password:
            raise ValueError(
                "EMAIL_USERNAME or EMAIL_PASSWORD environment variable not set."
            )

        # mail: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_username, email_password)
        mail.select("inbox")
        return mail

    def decode_header_value(self, value: str) -> str:
        """Decode email header value."""
        decoded, encoding = decode_header(value)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding or "utf-8")
        return decoded

    def parse_email(self, msg) -> dict:
        """Extract relevant information from an email message."""
        subject = self.decode_header_value(msg["Subject"]) if msg["Subject"] else "No Subject"
        sender = msg["From"]
        date = msg["Date"]

        # Parse email content
        body = ""
        attachment_content = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode("utf-8")
                if "attachment" in content_disposition and part.get_filename():
                    filename = part.get_filename()
                    if filename.endswith(".txt"):
                        attachment_content = part.get_payload(decode=True).decode("utf-8")

        else:
            body = msg.get_payload(decode=True).decode("utf-8")

        content = attachment_content if attachment_content else body

        return {
            "timestamp": date,
            "sender": sender,
            "subject": subject,
            "message": content.strip(),
        }

    def save_to_csv(self, data: dict):
        """Append email data to a CSV file."""
        with open(EMAIL_CSV, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([data["timestamp"], data["sender"], data["subject"], data["message"]])

    def email_already_logged(self, timestamp: str) -> bool:
        """Check if the email timestamp already exists in the CSV file."""
        try:
            with open(EMAIL_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                return any(row[0] == timestamp for row in reader)
        except FileNotFoundError:
            # If file doesn't exist, it's the first time writing
            return False

    def fetch_and_store_emails(self):
        """Fetch and process emails from Gmail."""
        mail = None
        try:
            # Connect to Gmail's IMAP server
            mail = self.connect_to_email()

            # Search for all emails
            _, messages = mail.search(None, f'(FROM "{os.getenv("EXPECTED_SENDER")}")')
            messages = messages[0].split()

            for msg_num in messages:  # Fetch the last 5 emails for testing
                _, msg_data = mail.fetch(msg_num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        try:
                            parsed_email = self.parse_email(msg)
                            if os.getenv("EXPECTED_SENDER") in parsed_email["sender"]:
                                if not self.email_already_logged(parsed_email["timestamp"]):
                                    self.save_to_csv(parsed_email)
                                    print(f"Saved email from {parsed_email['sender']} at time {parsed_email['timestamp']}")
                                else:
                                    print(f"Got duplicate email with timestamp {parsed_email['timestamp']}, breaking loop")
                                    return
                        except Exception as e:
                            print(f"Skipping email, got error {str(e)}")

        except Exception as e:
            print(f"Error fetching emails: {e}")

        finally:
            if mail:
                mail.logout()

    def connect_smtp(self):
        """Connect to the SMTP server."""
        try:
            server = smtplib.SMTP(SMTP_SERVER, 587)
            server.starttls()
            server.login(os.environ["EMAIL_USERNAME"], os.environ["EMAIL_PASSWORD"])
            return server
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            return None

    def send_message(self, body: str, subject: str = ""):
        """Send an email message."""
        try:
            # Set up the server and login
            server = self.connect_smtp()
            if server is None:
                print("Failed to send email. SMTP server connection error.")
                return

            # Create email message
            message = MIMEMultipart()
            message["From"] = os.environ["EMAIL_USERNAME"]
            message["To"] = os.environ["EXPECTED_SENDER"]
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Send the email
            server.sendmail(os.environ["EMAIL_USERNAME"], os.environ["EXPECTED_SENDER"], message.as_string())
            server.quit()

            print(f"Message sent to {os.environ['EXPECTED_SENDER']}")
        except Exception as e:
            print(f"Failed to send message: {e}")


if __name__ == "__main__":
    # EmailClient().fetch_and_store_emails()
    EmailClient().send_message("Test sending a messagem2")
