"""XP System for player"""
import pickle

from email_client import EmailClient


class XPSystem:
    """XP System for the player"""
    def __init__(self):
        self.total_xp = 0
        self.level = 0
        self.unlocked_titles = ["Tester"]
        self.title = "Tester"
        self.skills_xp = {"music": 0, "programming": 0, "social": 0, "life": 0, "physical": 0}
        self.skill_tree = {
            "programming": {
                "web-development": 0,
                "big-data": 0,
                "terminal": 0,
                "networking": 0,
                "general": 0,
            },
            "music": {
                "writing": 0,
                "production": 0,
                "singing": 0,
                "piano": 0,
                "violin": 0,
                "performing": 0,
            },
            "social": {
                "dating": 0,
                "friends": 0,
                "job": 0,
            },
            "physical": {
                "strength": 0,
                "sports": 0,
            },
            "life": {
                "chores": 0,
                "money": 0,
            }
        }
        self.actions = {
            "sing practice": {
                "skill": "music",
                "subskill": "singing",
                "xp": 10
            }
        }
        self.level_titles = {
            1: "Beginner",
            5: "Novice",
            10: "Demon Slayer",
            15: "Task Terminator",
            25: "XP Farmer",
            50: "Leviathan",
            100: "Demon King",
            150: "Dreamer",
            200: "Player"
        }
        self.filename = "rdas_stats.pkl"

    def send_message(self, msg: str):
        """Send string message"""
        print(msg)
        EmailClient().send_message(msg)

    def level_up(self) -> str:
        """See if user has levelled up or not"""
        # Taken from pokemon medium-fast levelling equation:
        # https://bulbapedia.bulbagarden.net/wiki/Experience
        while self.total_xp >= (self.level+1) ** 3:
            self.level += 1
            self.send_message("Level Up!\n")
        if self.level in [1, 5, 10, 15, 25, 50, 75, 100, 150, 200]:
            self.unlocked_titles.append(self.level_titles[self.level])
            self.title = self.unlocked_titles[-1]
            self.send_message(f"Unlocked new title: {self.title}")

    def equip_title(self, title: str):
        """Change title"""
        if title in self.unlocked_titles:
            self.title = title
            self.send_message(f"Updated title to {title}")
        else:
            self.send_message(f"Could not equip title, titles available to player are: {self.unlocked_titles}")

    def update_xp(self, xp: int, skill: str, subskill: str):
        """Update xp calculations for particular subskill"""
        self.skill_tree[skill][subskill] += xp
        self.skills_xp[skill] += xp
        self.total_xp += xp
        self.level_up()

    def add_action(self, skill: str, subskill: str, xp: int, action: str):
        """Add an action to registered actions"""
        if skill not in self.skills_xp:
            return
        if subskill not in self.skill_tree[skill].keys():
            return
        if action not in self.actions:
            self.actions[action] = {
                "skill": skill,
                "subskill": subskill,
                "xp": xp,
            }

    def performed_action(self, action: str):
        """Update xps after performing an action"""
        if action not in self.actions:
            return
        self.update_xp(
            self.actions[action]["xp"],
            self.actions[action]["skill"],
            self.actions[action]["subskill"]
        )
        self.save_progress(self.filename)

    def __str__(self) -> str:
        """Display the current status of XP and levels."""
        status = f"Current Level: {self.level} | Total XP: {self.total_xp}"
        status += (f"\nEquipped Title: {self.title}")
        for skill, xp in self.skills_xp.items():
            status += (f"\n\t{skill.capitalize()} Skill XP: {xp}")
            for sub_skill, xp in self.skill_tree[skill].items():
                status += (f"\n\t\t{skill.capitalize()} -> {sub_skill.capitalize()} XP: {xp}")
        return status

    def save_progress(self, filename):
        """Save progress to file"""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
            print(f"Progress saved to {filename}")

    def process_message(self, msg: str) -> None:
        """process an input text message"""
        print(f"Input: {msg}")
        if "!help" in msg:
            self.send_message(
                "List of messages:\n!status\n!add\n!title\n{action}"
            )
        elif "!status" in msg:
            self.send_message(str(self))
        elif "!add" in msg:
            msg = msg.split("!add ", 1)[-1]
            skill, subskill, xp, action = msg.split(" ", 3)
            xp = int(xp)
            self.add_action(skill, subskill, xp, action)
        elif "!title" in msg:
            self.equip_title(msg.split(" ", 1)[-1])
        elif msg in self.actions:
            self.performed_action(msg)
        else:
            print("Could not recognize command. Send \"!help\" for list of commands")

    @staticmethod
    def load_progress(filename: str):
        """Load the XP system state from a file."""
        try:
            with open(filename, 'rb') as f:
                xp_system = pickle.load(f)
                print(f"Progress loaded from {filename}")
                return xp_system
        except FileNotFoundError:
            print("No previous progress found. Starting fresh.")
            return XPSystem()  # Return a new XPSystem instance if no file exists


if __name__ == "__main__":
    xp_sys = XPSystem()
    print(xp_sys)
    xp_sys.process_message("sing practice")
    xp_sys.process_message("!title")
    xp_sys.process_message("!status")
    xp_sys.process_message("!help")
    xp_sys.process_message("!add music piano 10 practice piano")
    xp_sys.save_progress("test.pkl")
    print("Loading back up")
    xp_sys2 = XPSystem.load_progress("test.pkl")
    xp_sys2.process_message("practice piano")
    print(xp_sys2)
