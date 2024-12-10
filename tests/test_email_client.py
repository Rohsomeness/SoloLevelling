import unittest
from unittest.mock import patch, MagicMock, mock_open
from email_client import EmailClient, DiscordClient

class TestEmailClient(unittest.TestCase):

    @patch("email_client.os.getenv")
    @patch("email_client.imaplib.IMAP4_SSL")
    def test_connect_to_email(self, mock_imap, mock_getenv):
        """Test connecting to the email server."""
        mock_getenv.side_effect = lambda key: "test_username" if key == "EMAIL_USERNAME" else "test_password"
        mock_mail = mock_imap.return_value
        
        client = EmailClient()
        mail = client.connect_to_email()
        
        mock_getenv.assert_any_call("EMAIL_USERNAME")
        mock_getenv.assert_any_call("EMAIL_PASSWORD")
        mock_mail.login.assert_called_with("test_username", "test_password")
        mock_mail.select.assert_called_with("inbox")
        self.assertEqual(mail, mock_mail)

    @patch("email_client.decode_header")
    def test_decode_header_value(self, mock_decode):
        """Test decoding email headers."""
        mock_decode.return_value = [(b"Test Subject", "utf-8")]
        
        client = EmailClient()
        result = client.decode_header_value("=?utf-8?b?VGVzdCBTdWJqZWN0?=")
        
        self.assertEqual(result, "Test Subject")
        mock_decode.assert_called_with("=?utf-8?b?VGVzdCBTdWJqZWN0?=")
    
    @patch("email_client.csv.reader")
    @patch("email_client.open", new_callable=mock_open, read_data="timestamp,sender,subject,message")
    def test_email_already_logged(self, mock_file, mock_csv_reader):
        """Test checking if email already exists in CSV."""
        mock_csv_reader.return_value = iter([["2023-12-03", "sender", "subject", "message"]])
        
        client = EmailClient()
        result = client.email_already_logged("2023-12-03")
        
        self.assertTrue(result)
        mock_file.assert_called_with("emails.csv", "r", encoding="utf-8")
    
    @patch("email_client.open", new_callable=mock_open)
    @patch("email_client.csv.writer")
    def test_save_to_csv(self, mock_writer, mock_file):
        """Test saving email data to CSV."""
        mock_csv = mock_writer.return_value
        data = {"timestamp": "2023-12-03", "sender": "sender@example.com", "subject": "Test", "message": "This is a test"}
        
        client = EmailClient()
        client.save_to_csv(data)
        
        mock_file.assert_called_with("emails.csv", "a", newline="", encoding="utf-8")
        mock_csv.writerow.assert_called_with(["2023-12-03", "sender@example.com", "Test", "This is a test"])
    
    @patch("email_client.requests.post")
    @patch("email_client.os.getenv")
    def test_discord_send_message(self, mock_getenv, mock_post):
        """Test sending a message via Discord."""
        mock_getenv.side_effect = lambda key: "http://discord.webhook" if key == "DISCORD_WEBHOOK" else "some_other_value"
        mock_post.return_value.status_code = 204

        with patch.dict('os.environ', {'DISCORD_WEBHOOK': 'http://discord.webhook'}):
            discord_client = DiscordClient()
            discord_client.send_message("Test message")
            
            mock_post.assert_called_with(
                "http://discord.webhook",
                json={"content": "Test message"},
                timeout=10
            )
            self.assertEqual(mock_post.return_value.status_code, 204)


if __name__ == '__main__':
    unittest.main()
