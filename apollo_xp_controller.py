import time

from email_client import DiscordClient
from xp_system import XPSystem


class ApolloXPController:
    """Manages email polling and XP system integration."""
    def __init__(self):
        """
        Initialize the ApolloXPController.

        Args:
            email_client (EmailClient): An instance of the EmailClient class.
            xp_system (XPSystem): An instance of the XPSystem class.
            poll_interval (int): Time interval (in seconds) for polling emails.
        """
        self.email_client = DiscordClient()
        self.filename = "rdas_player.pkl"
        self.xp_system = XPSystem.load_progress(self.filename)
        self.poll_interval_s = 10

    def run(self):
        """Run program"""
        print("Starting Apollo Controller")
        while True:
            new_email_messages = self.email_client.fetch_and_store_emails()
            for new_message in new_email_messages:
                self.xp_system.process_message(new_message)
            time.sleep(self.poll_interval_s)
