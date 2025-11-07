import logging
logging.basicConfig(level=logging.DEBUG) 

class UserIfo:
    def __init__(self):
        self._name = ""
        self._title = ""
        self._overAll_level = 0
        self.subjects = {}  # {"math": {"level": 0}, ...}
        
    # Basic getters and setters 
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
        if name[0].istitle():
            self._name = name
        else:
            return "Please capitalize the leter of your name"   
    
    @title.setter
    def title(self, title):
        self._title = title

    @level.setter
    def level(self, total):
        pass

    def initialize_subjects(self, subject_list):
        for subject in subject_list:
            self.subjects[subject] = {"level": 0}

    def level_up_subject(self, subject, new_level):
        if subject in self.subjects:
            self.subjects[subject]["level"] = new_level
            logging.debug(f"🎉 {subject} leveled up to {new_level}!")
        else:
            logging.debug(f"🚫 Subject {subject} not found.")

    def update_overall_level(self):
        total_levels = sum(subject["level"] for subject in self.subjects.values())
        new_overall = total_levels // 5
        if new_overall > self._overAll_level:
            logging.debug(f"🏆 Overall level up! {self._overAll_level} → {new_overall}")
            self._overAll_level = new_overall

class AutodidexBank:
    def __init__(self, user_info):
        self._wallet_total = 0
        self._xp_total = 0
        self.badges = {}
        self._subjectXp = {}
        self.user_info = user_info  # <<<< Correct usage!

        # Initialize subject XP based on user_info's subjects
        for subject in self.user_info.subjects:
            self._subjectXp[subject] = 0
        
    @property
    def wallet(self):
        return self._wallet_total
    
    @property
    def xpXpoints(self):
        return self._xp_total
    
    @wallet.setter
    def wallet(self, lumens):
        if lumens < 0:
            return "You cannot deposit negative lumens"
        else:
            self._wallet_total += lumens
    
    @xpXpoints.setter
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

    # Properties like before...

    def earn_subject_xp(self, subject, points):
        """User earns XP in a specific subject."""
        if subject not in self._subjectXp:
            logging.debug(f"🚫 Subject '{subject}' not found in bank.")
            return

        # Update XP
        self._subjectXp[subject] += points
        logging.debug(f"✨ Earned {points} XP in {subject}! Total: {self._subjectXp[subject]} XP.")

        # Check if level-up happened
        new_level = self._subjectXp[subject] // 100
        current_level = self.user_info.subjects[subject]["level"]
        if new_level > current_level:
            self.user_info.level_up_subject(subject, new_level)
            self.user_info.update_overall_level()
