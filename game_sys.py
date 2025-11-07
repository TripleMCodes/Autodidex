import logging
logging.basicConfig(level=logging.DEBUG) 

class UserIfo:

    def __init__(self):
        self._name = ""
        self._title = ""
        self._overAll_level = 0
        self.subjects = {}
        
     #getters
    @property
    def name(self):
        return self._name
    
    @property
    def title(self):
        return self._title
    
    @property
    def level(self):
        return self._overAll_level
    
    @name.setter
    def name(self, name):
        if name and name[0].isupper():
            self._name = name
        else:
            raise ValueError("Please capitalize the first letter of your name")
    
    
    @title.setter
    def title(self, title):
        self._title = title

    @level.setter
    def level(self, total):
        pass

    def initialize_subjects(self):
            for key in self.subjects:
                self.subjects[key]["level"] = 0

    def subject_level_up(self, userBank, subject):
        """Increase the user's level, you level up every hundred points earned."""
        if subject not in self.subjects:
            logging.debug(f"Subject '{subject}' not found.")
            return False
        if subject not in userBank.subjectXp:
            logging.debug(f"No XP data for '{subject}' in userBank.")
            return False
        
        new_level = userBank.subjectXp[subject] // 100
        if new_level > self.subjects[subject]["level"]:
            self.subjects[subject]["level"] = new_level
            logging.debug(f"🎉 {subject} leveled up to {new_level}!")
            #earning lumens
            userBank.wallet(10)
            logging.debug(f"Income: 10 Lumens\nAccount balance: {userBank.wallet}")
            return True
        return False


    def overall_level_up(self, userBank):
        """Sum all subject XP points, each new gain of 500 XP points gives 1 overall level up."""
    
        # Calculate the new overall level based on total XP
        new_overall_level = userBank.xpPoints // 500
        
        # Check if the overall level has increased
        if new_overall_level > self._overAll_level:
            self._overAll_level = new_overall_level
            logging.debug(f"🏆 Overall level up! {self._overAll_level - 1} → {self._overAll_level}")
            return True  # Return True if level-up happens
        else:
            logging.debug(f"🔄 No overall level-up yet. Current XP: {userBank.xpPoints}")
            return False  # Return False if no level-up happens


    def check_for_badges(self, userBank):
        """Check if user qualifies for a badge and award it."""
        # Example condition for level-based badges
        if self._overAll_level >= 10 and "Level 10 Badge" not in userBank.badges:
            userBank.badges.append("Level 10 Badge")
            logging.debug("🎉 You earned the Level 10 Badge!")
        
        # Example condition for XP-based badges
        if userBank.xpPoints >= 1000 and "1000 XP Badge" not in userBank.badges:
            userBank.badges.append("1000 XP Badge")
            logging.debug("🎉 You earned the 1000 XP Badge!")
            userBank.wallet = 5
            logging.debug(f"Income: 5 lumens\nAccount balance: {userBank.wallet}")
        
        # Example condition for subject mastery badge
        for subject in self.subjects:
            if self.subjects[subject]["level"] >= 10 and f"{subject} Master" not in userBank.badges:
                userBank.badges.append(f"{subject} Master")
                logging.debug(f"🎉 You earned the {subject} Master Badge!")
                userBank.wallet = 10  # Will trigger setter to add 10 lumens
                logging.debug(f"Income: 10\nAccount Balance: {userBank.wallet}")
        
            
class AutodidexBank:
    
    def __init__(self, user_info):
        self._wallet_total = 0
        self._xp_total = 0
        self.badges = [] 
        self._subjectXp = {}
        for key in user_info.subjects:
            self._subjectXp[key] = 0
        self.user_info = UserIfo()


    @property
    def wallet(self):
        return self._wallet_total
    
    @property
    def xpPoints(self):
        return self._xp_total
    
    @wallet.setter
    def wallet(self, lumens):
        if lumens < 0:
            return "You cannot deposit negative lumens"
        else:
            self._wallet_total += lumens
    
    @xpPoints.setter
    def xpPoints(self, points):
        if points < 0:
            return "You cannot earn negative xp points"
        else:
            self._xp_total += points

    @property
    def subjectXp(self):
        return self._subjectXp
    
    @subjectXp.setter
    def subjecXp(self, points):
        if points < 0:
            return "You cannot earn negative xp points"
        else:
            self._xp_total += points

    def earn_subject_xp(self, subject, userbank): #userBank is Autodidex
        """User earns XP in a specific subject."""
        if subject not in self.user_info.subjects:
            logging.debug(f"Subject '{subject}' not found.")
            return
        # self.userBank.add_subject_xp(subject)
        self.user_info.subject_level_up( userbank, subject)
        self.user_info.overall_level_up()

    def spend_lumens(self, amount):

        self._wallet_total = self._wallet_total - amount
        return True
        
    def add_subject_xp(self, subject, points):
        if subject in self._subjectXp:
            self._subjectXp[subject] += points
            self._xp_total += points
        else:
            logging.debug(f"⚠️ Subject '{subject}' not found in XP tracker.")


class PolyMart:

    def __init__(self, bank_account):
        self.bank_account = bank_account
        self.store_items = {
            "Day-off": 1000,
            "half Day-off": 500,
            "15 min off from any subject": 250,
            "1 song/vid while studying": 100
        }

        self.badge_trade_values = {
            "Level 10 Badge": 50,
            "1000 XP Badge": 100
        }

    def purchase_item(self, item_name):
        if item_name not in self.store_items:
            print("❌ Item not found in PolyMart.")
            return

        cost = self.store_items[item_name]
        if self.bank_account.lumens >= cost:
            self.bank_account.spend_lumens(cost)
            print(f"🛒 You bought {item_name} for {cost} lumens!")
        else:
            print("💸 Not enough lumens!")

    def trade_badge_for_lumens(self, badge_name):
        if badge_name not in self.badge_trade_values:
            print("❌ Invalid badge.")
            return

        if badge_name in self.bank_account.badges:
            self.bank_account.badges.remove(badge_name)
            value = self.badge_trade_values[badge_name]
            self.bank_account.wallet = value
            print(f"🔁 Traded {badge_name} badge for {value} lumens.")
        else:
            print(f"🚫 You don't have a {badge_name} badge.")



    
    
# data = {
#     "programming": {
#         "chapter one": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter two": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter three": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter four":{
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         }
#         },
#     "mathematics": {
#         "chapter one": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter two": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter three": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         },
#         "chapter four": {
#             "topic 1": "date of completion",
#             "topic 2": "date of completion",
#             "topic 3": "date of completion",
#         }
#         },
# }