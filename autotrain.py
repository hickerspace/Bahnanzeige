import lxml.html
import urllib
import urllib2
import cookielib
import datetime
import re
from train import AutoTrain

ORIGIN = "L1A"
DESTINATION = "L1D"

TYPES = [ ORIGIN, DESTINATION ]

class AutoTrainRequest(object):

	def __init__(self, station, dt=datetime.datetime.today()):
		self.station = station
		self.dt = dt
		self.trainList = [ ]

		for TYPE in TYPES:
			self.request(TYPE)


	def request(self, TYPE):
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

		# 1st step: set station we're interested in and get all connected stations
		step1 = opener.open("http://buchung.dbautozug.de/book/0.asp?%s=%s" % (TYPE, self.station))
		step1html = step1.read()
		step1Tree = lxml.html.fromstring(step1html)

		originElem = "select/option" if (TYPE == ORIGIN) else "input"
		destinationElem = "input" if (TYPE == ORIGIN) else "select/option"

		firstField = step1Tree.xpath("/html/body/div/table/tr/td/div/form/table[4]/tbody/tr/td/table/tbody/tr[2]/td[3]/%s" % originElem)
		firstField = map(lambda field: field.get("value"), firstField)[1:] if len(firstField) > 1 else firstField[0].get("value")

		secondField = step1Tree.xpath("/html/body/div/table/tr/td/div/form/table[4]/tbody/tr/td/table/tbody/tr[3]/td[3]/%s" % destinationElem)
		secondField = map(lambda field: field.get("value"), secondField)[1:] if len(secondField) > 1 else secondField[0].get("value")

		# determine origin and destination
		if isinstance(firstField, basestring):
			location = firstField
			origins = secondField
		else:
			location = secondField
			origins = firstField

		for origin in origins:
			# 2nd step: cycle through connections
			opener.open("https://buchung.dbautozug.de/book/1.asp", "frmName=frmFormAZDB1&L1Da=%s&L1Aa=%s&SR=S&L2Da=%s&L2Aa=%s&selVehType=CAR%%2F500%%2F205&vehNum=1&WeightGT1500=N&WeightGT1500R=1500&WeightGT1500R=1501&NA=1&NC=0&NI=0&btnsubmit=Weiter" % (origin, location, location, origin))

			# 3rd step: provide pseudo data to satisfy DB and retrieve available months
			step3 = opener.open("https://buchung.dbautozug.de/book/2.asp", "sd=352867002&submitFrom=VH&frmName=frmFormAZDB2&DoNext=&mbPromCode1=&mbClientNum1=&mbClientEmail1=&mbPartnerID1=&mbDepPort11=%s&mbDestPort11=%s&mbDepPort12=&mbDestPort12=&mbSingle1=S&mbDiffL1L2Acc1=&mbNumAdults1=1&mbNumChildren1=0&mbNumInfants1=0&mbVehNum11=1&mbVehNum12=0&mbVehType111=CAR&mbVehType112=&mbVehType113=&mbVehType114=&mbVehType115=&mbVehType116=&mbVehType121=&mbVehType122=&mbVehType123=&mbVehType124=&mbVehType125=&mbVehType126=&onRoof=n&selRoofWidth=135&selVehHeight=158%%2F20050101%%2F20130322%%2Fefb" % (origin[:-2], location[:-2]))
	
			step3Tree = lxml.html.fromstring(step3.read())

			months = step3Tree.xpath("/html/body/div/table/tr/td/form/table[5]/tbody/tr[3]/td/table/tbody/tr[2]/td/select/option")
			months = map(lambda month: month.get("value"), months)

			if not self.dt.strftime("%Y%m") in months:
				continue
	
			# cycle through available months
			clickMonth = opener.open("https://buchung.dbautozug.de/book/2.asp", "sd=352867326&submitFrom=L1&frmName=frmFormAZDB2&DoNext=&mbPromCode1=&mbClientNum1=&mbClientEmail1=&mbPartnerID1=&mbDepPort11=%s&mbDestPort11=%s&mbDepPort12=&mbDestPort12=&mbSingle1=S&mbDiffL1L2Acc1=&mbNumAdults1=1&mbNumChildren1=0&mbNumInfants1=0&mbVehNum11=1&mbVehNum12=0&mbVehType111=CAR&mbVehType112=&mbVehType113=&mbVehType114=&mbVehType115=&mbVehType116=&mbVehType121=&mbVehType122=&mbVehType123=&mbVehType124=&mbVehType125=&mbVehType126=&onRoof=n&selRoofWidth=135&selVehHeight=158%%2F20050101%%2F20130322%%2Feb&part2=Y&selLeg1YYYYMM=%s" % (origin[:-2], location[:-2], self.dt.strftime("%Y%m")))
		
			clickMonthTree = lxml.html.fromstring(clickMonth.read())

			journeys = clickMonthTree.xpath("/html/body/div/table/tr/td/form/table[5]/tbody/tr[3]/td/table/tbody/tr[*]/td/input")
			journeys = map(lambda journey: urllib.urlencode({ "selLeg1Det" : journey.get("value"), "selLeg1YYYYMM" : self.dt.strftime("%Y%m") }), journeys)

			for journey in journeys:
				# retrieve data for each connection
				step4 = opener.open("https://buchung.dbautozug.de/book/2.asp", "sd=352867002&submitFrom=&frmName=frmFormAZDB2&DoNext=NEXT&mbPromCode1=&mbClientNum1=&mbClientEmail1=&mbPartnerID1=&mbDepPort11=%s&mbDestPort11=%s&mbDepPort12=&mbDestPort12=&mbSingle1=S&mbDiffL1L2Acc1=&mbNumAdults1=1&mbNumChildren1=0&mbNumInfants1=0&mbVehNum11=1&mbVehNum12=0&mbVehType111=CAR&mbVehType112=&mbVehType113=&mbVehType114=&mbVehType115=&mbVehType116=&mbVehType121=&mbVehType122=&mbVehType123=&mbVehType124=&mbVehType125=&mbVehType126=&onRoof=n&selRoofWidth=135&selVehHeight=158%%2F20050101%%2F20130322%%2Fefb&part2=Y&%s&btnSubmit=Weiter" % (origin[:-2], location[:-2], journey))

				schedule = lxml.html.fromstring(step4.read())

				# skip if an error occurred
				if len(schedule.xpath("//td[@class='ErrorMessage']")) > 0:
					continue

				name, trainOrigin = schedule.xpath("/html/body/div/table/tr/td/form/table[3]/tbody/tr[2]/td[2]")[0].text.encode("utf8").replace("\r\n", "").replace("\t", "").replace("\xc2\xa0", "").split(":")
				destination = schedule.xpath("/html/body/div/table/tr/td/form/table[3]/tbody/tr[2]/td[2]/img")[0].tail.encode('utf8').replace("\r\n", "").replace("\xc2\xa0", "")[:-2]
				arrival = schedule.xpath("/html/body/div/table/tr/td/form/table[3]/tbody/tr[3]/td[3]")[0].text.encode('utf8').replace("\r\n", "").replace("\t", "").replace("\xc2\xa0", "")

				if TYPE == ORIGIN:
					searchFor = "Ankunft"
				else:
					searchFor = "Abfahrt"

				arrival = re.findall(r"%s (\d\d.\d\d. \d\d:\d\d)" % searchFor, arrival)[0]
				arrival = datetime.datetime.strptime("%s %d" % (arrival, self.dt.year), "%d.%m. %H:%M %Y")

				self.trainList.append(AutoTrain(self.station, self.dt, name, trainOrigin, destination, arrival))

	def getTrainList(self):
		return self.trainList

def main():
	# return trains for Hildesheim Hbf
	freightTrains = AutoTrainRequest("Hildesheim")
 
	for train in freightTrains.getTrainList():
		print train

if __name__ == '__main__':
	main()


