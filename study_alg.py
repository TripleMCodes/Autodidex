###Study program
import time
import pyinputplus as pyip
import datetime
from typing import Optional
import os
import sys

class StudyingAlgorithm():
	
	def __init__(self):
		self.state: Optional[str] = "energized"
		self.fatigue_level = Optional[str] = None
		self.study_time: Optional[int] = 0
		self.fatigue_levels = {
                        "level 0": None,
						"level 1": 5,
						"level 2": 15,
						"level 3": 30
					}
		self.subjects = {
						"Primary": [
									"Mathematics",
									"Physics",
									"Programming",
									"Writing"
								],
						"Secondary":[
									"Linguistics",
									"Korean",
									"Designing",
									"Reading"
								],
						"Tertiary":[
									"Recitation",
									"Anki",
									"Connor's Crazy Cognitions"
							      ]
					}
		self.wrapper()									
						
	def fatigue(self):
		"""Test for my level of fatigue and recommand needed rest
		 before getting back or starting studying"""
		if self.state != "energized":
			fatigue_level = self.fatigue_levels[self.fatigue_level]
			self.timer(fatigue_level)
		self.state = "energized"
		return True
			
	def timer(self, time: int):
		"""basic timer for the rest I need"""
		now = datetime.datetime.now()
		rest_time = now + datetime.timedelta(minutes=time)

		while datetime.datetime.now() < rest_time:
			remaining_time = (rest_time - datetime.datetime.now()).seconds
			sys.stdout.write(f"\rTime Left: {remaining_time // 60}:{remaining_time % 60:02d}")
			sys.stdout.flush()
			time.sleep(1)
	
	def study_secession_setting(self):
		"""check for the time available that I have to study,
			and then recommand how I should study"""
		
		return 

	def study_time_available(self):
		"""checks for the study time I have, and then recommands how I should study"""
		
	def wrapper(self):
		state = pyip.inputChoice(["energized", "fatigued"], "Enter how you  feel today")
		self.state = state
		if self.state == "fatigued":
			fatigue_level = pyip.inputChoice(["leve 0","level 1", "level 2", "level 3"], "Enter your fatigue level today")
			self.state = fatigue_level
		study_time_available = pyip.inputInt("Enter the study available today: ")
		self.study_time = study_time_available
		