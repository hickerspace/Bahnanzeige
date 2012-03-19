#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
		direction, scheduledPlatform, actualTime, actualPlatform):

		Train.__init__(self, stationID, dt, name)

		self.category = category
		self.product = product

		self.scheduledTime = scheduledTime
		self.direction = direction
		self.scheduledPlatform = scheduledPlatform
 
		self.actualTime = actualTime
		self.actualPlatform = actualPlatform


class FreightTrain(Train):

	def __init__(self, stationID, dt, name, origin, arrival, departure):

		Train.__init__(self, stationID, dt, name)

		self.origin = origin
		self.arrival = arrival
		self.departure = departure
