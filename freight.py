#!/usr/bin/env python
# -*- coding: utf-8 -*-

from train import FreightTrain
import lxml.html
import datetime
import urllib2

REQUEST_USERAGENT = ""

class FreightTrainRequest(object):

	def __init__(self, stationID, dt=datetime.datetime.today()):

		self.stationID = stationID
		self.dt = dt
		self.trainList = [ ]

		# check arrivals and departures
		for boardType in ["arr", "dep"]:

			req = urllib2.Request(url="http://gueterfahrplan.hacon.de/bin/db/stboard.exe/dn?input=%s&boardType=%s&time=%s&maxJourneys=200&dateBegin=%s&dateEnd=%s&selectDate=&productsFilter=0&start=yes&" 
				% (stationID, boardType, dt.strftime("%H:%M"), dt.strftime("%d.%m.%Y"), dt.strftime("%d.%m.%Y")), headers={"User-Agent": REQUEST_USERAGENT})

			bahnResponse = urllib2.urlopen(req)			 
			freightTrainSchedule = lxml.html.fromstring(bahnResponse.read())

			# skip if an error occurred
			if len(freightTrainSchedule.xpath("//div[@class='errormessage']")) > 0:
				continue
	
			journeys = freightTrainSchedule.xpath("/html/body/table/tr[3]/td[2]/table/tr/td[2]/div/table[5]/tr[*]/td[3]/a[1]")
			journeys = map(lambda journey: journey.text.encode('utf8'), journeys)
			journeys = map(lambda journey: journey.replace("\n", ""), journeys)

			departures = freightTrainSchedule.xpath("/html/body/table/tr[3]/td[2]/table/tr/td[2]/div/table[5]/tr[*]/td[1]")
			departures = map(lambda departure: departure.text.encode('utf8'), departures)
			departures = map(lambda departure: departure.replace("\n", "").replace("(", "").replace(")", ""), departures)

			# do it the long way to get proper error management
			arrivals = [ ]
			for i in range (0, len(departures)):
				try:
					arrivals.insert(i, departures[i].split("\xc2\xa0")[0])
					departures[i] = departures[i].split("\xc2\xa0")[1]
				except IndexError:
					# ignore "journeys as necessary"
					pass

			origins = freightTrainSchedule.xpath("//html/body/table/tr[3]/td[2]/table/tr/td[2]/div/table[5]/tr[*]/td[4]/a/img")
			origins = map(lambda origin: origin.tail.encode('utf8'), origins)

			# create FreightTrain objects
			for i in range(0, len(journeys), 1):
				# ignore "journeys as necessary"
				if not journeys[i] == "Bedarf":
					self.trainList.append(FreightTrain(stationID, self.dt, journeys[i], origins[i], self.timeStringToDateTime(arrivals[i]), self.timeStringToDateTime(departures[i])))


	def timeStringToDateTime(self, timeString):
		hour, minute = timeString.split(":")
		timeObj = datetime.time(int(hour), int(minute))

		if timeObj >= self.dt.time():
			return datetime.datetime.combine(self.dt.date(), timeObj)
		else:
			return datetime.datetime.combine(self.dt.date() + datetime.timedelta(days=1), timeObj)


	def getTrainList(self):
		return self.trainList


def main():
	# return trains for Hildesheim Hbf
	freightTrains = FreightTrainRequest(180134148)
 
	for train in freightTrains.getTrainList():
		print train

if __name__ == '__main__':
	main()

