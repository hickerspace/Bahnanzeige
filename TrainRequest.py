#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

class PassengerTrainRequest(object):
 
	def __init__(self, stationID, dt=datetime.datetime.today()):

		self.userAgent = "" 
		self.stationID = stationID
		self.dt = dt
 
		self.trainList = []
