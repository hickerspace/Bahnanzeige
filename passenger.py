#!/usr/bin/env python
# -*- coding: utf-8 -*-

from train import PassengerTrain
import lxml.etree
import datetime
import urllib2

REQUEST_USERAGENT = ""

class PassengerTrainRequest(object):
 
	def __init__(self, stationID, dt=None):
 
		self.stationID = stationID
		self.dt = dt if dt else datetime.datetime.now()
		self.trainList = []
 
		self.doRequest("DEP")
		self.doRequest("ARR")


	def doRequest(self, prod):

		requestStr = """<?xml version='1.0' encoding='iso-8859-1'?>
<ReqC ver='1.1' prod='JP' lang='de' clientVersion='2.1.6'>
<STBReq boardType='%s' detailLevel='2'>
<Time>%s</Time>
<Period>
<DateBegin>%s</DateBegin>
<DateEnd>%s</DateEnd></Period>
<TableStation externalId='%s'/>
<ProductFilter>1111100000000000</ProductFilter>
</STBReq>
</ReqC>""" % (prod, self.dt.strftime("%H:%M:%S"), self.dt.strftime("%Y%m%d"), self.dt.strftime("%Y%m%d"), self.stationID)
 
		req = urllib2.Request(
			url="http://reiseauskunft.bahn.de/bin/mgate.exe",
			data=requestStr,
			headers={"User-Agent":REQUEST_USERAGENT})
 
		bahnResponse = urllib2.urlopen(req)
		bahnResponseStr = bahnResponse.read()
 
		bahnResponseXML = lxml.etree.fromstring(bahnResponseStr)
 
		bahnResponseEntries = bahnResponseXML.xpath("//Entries/StationBoardEntry")
 
		for entry in bahnResponseEntries:
			# do not return canceled trains
			infoMessages = entry.xpath("Messages/Message")
			infoMessages = map(lambda info: info.attrib["text"].encode("utf-8"), infoMessages)
			if "Zug f\xc3\xa4llt aus" in infoMessages:
				break
			 
			self.trainList.append(PassengerTrain(
				self.stationID,
				self.dt,
				entry.attrib["category"], 
				entry.attrib["product"],
				entry.attrib["name"],
				entry.attrib["scheduledTime"], 
				entry.attrib["direction"].encode("utf-8"),
				entry.attrib["scheduledPlatform"],
				entry.attrib.get("actualTime", default=None),
				entry.attrib.get("actualPlatform", default=None),
				prod))


	def getTrainList(self):
		return self.trainList
 
def main():
	tReq = PassengerTrainRequest(8000169) # id stands for Hildesheim Hbf
 
	for train in tReq.getTrainList():
		print train

if __name__ == '__main__':
	main()
