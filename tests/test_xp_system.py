import unittest
from unittest.mock import patch
from xp_system import XPSystem


class TestXPSystem(unittest.TestCase):

    def setUp(self):
        """Set up a fresh XPSystem instance before each test."""
        self.xp_system = XPSystem()

    @patch('xp_system.DiscordClient.send_message')
    def test_initial_state(self, mock_send_message):
        """Test the initial state of the XP system."""
        self.assertEqual(self.xp_system.total_xp, 0)
        self.assertEqual(self.xp_system.level, 0)
        self.assertEqual(self.xp_system.title, "Tester")
        self.assertEqual(self.xp_system.skills_xp, {"music": 0, "programming": 0, "social": 0, "life": 0, "physical": 0})

    @patch('xp_system.DiscordClient.send_message')
    def test_level_up(self, mock_send_message):
        """Test leveling up logic."""
        self.xp_system.level = 3
        self.xp_system.total_xp = 9  # 9 XP should not level up the player
        self.xp_system.level_up()
        self.assertEqual(self.xp_system.level, 3)

        self.xp_system.total_xp = 1000  # 1000 XP should level up the player multiple times
        self.xp_system.level_up()
        self.assertEqual(self.xp_system.level, 10)

    @patch('xp_system.DiscordClient.send_message')
    def test_add_action(self, mock_send_message):
        """Test adding a new action."""
        self.xp_system.add_action('music', 'singing', 20, 'karaoke')
        self.assertIn('karaoke', self.xp_system.actions)

    @patch('xp_system.DiscordClient.send_message')
    def test_performed_action(self, mock_send_message):
        """Test performing an action."""
        initial_xp = self.xp_system.total_xp
        self.xp_system.performed_action('sing practice')
        self.assertEqual(self.xp_system.total_xp, initial_xp + 10)

    @patch('xp_system.DiscordClient.send_message')
    def test_equip_title(self, mock_send_message):
        """Test equipping a new title."""
        self.xp_system.level = 10
        self.xp_system.level_up()
        self.xp_system.equip_title("Demon Slayer")
        self.assertEqual(self.xp_system.title, "Demon Slayer")

    @patch('xp_system.DiscordClient.send_message')
    def test_show_actions(self, mock_send_message):
        """Test showing actions for a specific skill."""
        self.xp_system.show_actions('music')
        mock_send_message.assert_called()

    @patch('xp_system.DiscordClient.send_message')
    def test_save_and_load_progress(self, mock_send_message):
        """Test saving and loading progress."""
        self.xp_system.total_xp = 100
        self.xp_system.save_progress('test_save.pkl')
        loaded_system = XPSystem.load_progress('test_save.pkl')
        self.assertEqual(loaded_system.total_xp, 100)


if __name__ == '__main__':
    unittest.main()
