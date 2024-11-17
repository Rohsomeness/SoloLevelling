"""Scrape email account to find texts that were sent"""
import os
import imaplib
import email


def connect_to_email() -> imaplib.IMAP4_SSL:
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


def fetch_last_five_emails(mail: imaplib.IMAP4_SSL) -> None:
    """
    Fetch and print the subjects of the last 5 emails from the inbox.

    Args:
        mail (imaplib.IMAP4_SSL): The connection object for the IMAP server.

    Returns:
        None
    """
    # Search for all emails in the inbox
    _, messages = mail.search(None, "ALL")
    message_ids = messages[0].split()

    # Fetch the last 5 emails
    for msg_id in message_ids[-5:]:
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                print(f"Subject: {msg['subject']}")


if __name__ == "__main__":
    try:
        mail_client = connect_to_email()
        fetch_last_five_emails(mail_client)
    except Exception as e:
        print(f"Error: {e}")
