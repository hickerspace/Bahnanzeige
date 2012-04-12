#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re

class Train(object):
 
	def __init__(self, stationID, dt, name):
 
		self.stationID = stationID
		self.dt = dt

		self.name = name
		
	# replace with something smarter
	def __str__(self):
		return str(self.__dict__)


class PassengerTrain(Train):

	def __init__(self, stationID, dt, category, product, name, scheduledTime, 
		direction, scheduledPlatform, actualTime, actualPlatform, prod):

		Train.__init__(self, stationID, dt, re.sub(" +", " ", name))

		self.category = category
		self.product = product
		self.direction = direction

		self.scheduledTime = self.timeStringToDateTime(scheduledTime)
		self.scheduledPlatform = scheduledPlatform
 
		self.actualTime = self.timeStringToDateTime(actualTime)
		self.actualPlatform = actualPlatform

		self.prod = prod

		if actualTime:
			self.delayed = True
		else:
			self.delayed = False


	def timeStringToDateTime(self, timeString):

		if timeString is None:
			return None

		hour, minute = timeString.split(":")
		timeObj = datetime.time(int(hour), int(minute))

		if timeObj < self.dt.time():
			return datetime.datetime.combine(self.dt.date() + datetime.timedelta(days=1), timeObj)
		else:
			return datetime.datetime.combine(self.dt.date(), timeObj)

	def __str__(self):
		displayPlatform = self.actualPlatform if self.actualPlatform else self.scheduledPlatform
		delayedStr = " (verspätet)" if self.delayed else ""

		return "%s an Gleis %s nach %s%s" % (self.name, displayPlatform, self.direction, delayedStr)

class FreightTrain(Train):

	def __init__(self, stationID, dt, name, origin, arrival, departure):

		Train.__init__(self, stationID, dt, name)

		self.origin = origin
		self.arrival = arrival
		self.departure = departure

	def __str__(self):
		# FIXME: arrival only
		return "Güterzug %s von %s" % (self.name, self.origin)


class AutoTrain(Train):

	def __init__(self, stationID, dt, name, origin, destination, arrival):

		Train.__init__(self, stationID, dt, name)

		self.origin = origin
		self.destination = destination
		self.arrival = arrival

	def __str__(self):
		return "Autozug %s von %s nach %s" % (self.name, self.origin, self.destination)
