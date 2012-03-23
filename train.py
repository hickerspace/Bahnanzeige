#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re

class Train(object):
 
	def __init__(self, stationID, dt, name):
 
		self.stationID = stationID
		self.dt = dt

		self.name = re.sub(" +", " ", name)
		
	# replace with something smarter
	def __str__(self):
		return str(self.__dict__)


class PassengerTrain(Train):

	def __init__(self, stationID, dt, category, product, name, scheduledTime, 
		direction, scheduledPlatform, actualTime, actualPlatform, prod):

		Train.__init__(self, stationID, dt, name)

		self.category = category
		self.product = product
		self.direction = direction

		self.scheduledTime = self.timeStringToDateTime(scheduledTime)
		self.scheduledPlatform = scheduledPlatform
 
		self.actualTime = self.timeStringToDateTime(actualTime)
		self.actualPlatform = actualPlatform

		self.prod = prod


	def timeStringToDateTime(self, timeString):

		if timeString is None:
			return None

		hour, minute = timeString.split(":")
		timeObj = datetime.time(int(hour), int(minute))

		if timeObj < self.dt.time():
			return datetime.datetime.combine(self.dt.date() + datetime.timedelta(days=1), timeObj)
		else:
			return datetime.datetime.combine(self.dt.date(), timeObj)




class FreightTrain(Train):

	def __init__(self, stationID, dt, name, origin, arrival, departure):

		Train.__init__(self, stationID, dt, name)

		self.origin = origin
		self.arrival = arrival
		self.departure = departure