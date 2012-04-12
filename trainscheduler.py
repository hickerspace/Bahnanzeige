import datetime
import time

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.shelve_store import ShelveJobStore
import apscheduler.events

import passenger
import freight
import autotrain

import logging

CHECKBEFORE = 10
AUTO_TRAIN_STATION_NAME = "Hildesheim"
PASSENGER_STATION_ID = 8000169
FREIGHT_STATION_ID = 180134148
OUTPUT_FILE = "ledticker.txt"

class TrainScheduler(object):
 
	def __init__(self):
		logging.basicConfig(level=logging.DEBUG, filename="debug.log", format='%(asctime)s %(levelname)-8s %(message)s', datefmt="%d.%m.%Y %H:%M:%S")

		self.scheduler = Scheduler()
		self.scheduler.add_listener(self.checkForDuplicates, apscheduler.events.EVENT_JOBSTORE_JOB_ADDED)
		self.scheduler.start()

		if len(self.scheduler.get_jobs()) == 0:
			self.createInitSchedule()

		self.log("Initial tasks completed. Waiting for next event..")

		while True:
			try:
				time.sleep(10)
				#self.scheduler.print_jobs()

			except KeyboardInterrupt:
				self.log("Shutting down..")
				self.scheduler.shutdown()
				quit()


	def createInitSchedule(self):

		self.log("Perform initial query for passenger trains..")
		self.processPassenger()
		self.log("Perform initial query for freight trains..")
		self.processFreight()
		self.log("Perform initial query for auto trains..")
		self.processAutotrain()

		self.log("Creating initial train schedule..")
		
		# passenger
		self.scheduler.add_cron_job(self.processPassenger, hour="*/1", minute="0", day="*", month="*", year="*")
		# freight
		self.scheduler.add_cron_job(self.processFreight, hour="0", minute="2", day="*", month="*", year="*")
		# autotrain
		self.scheduler.add_cron_job(self.processAutotrain, hour="0", minute="5", day="1", month="*", year="*")


	def processPassenger(self):
		# return trains for station in question
		tReq = passenger.PassengerTrainRequest(PASSENGER_STATION_ID)
		self.log("Requesting passenger trains since %s." % tReq.dt)
	 
		for train in tReq.getTrainList():
			trainTime = train.actualTime if (train.actualTime) else train.scheduledTime
			trainTimeCheck = trainTime - datetime.timedelta(minutes=CHECKBEFORE)
						
			try:
				self.scheduler.add_date_job(self.checkIfOnTime, trainTimeCheck, args=[train], name=train.name)
				self.log("Schedule passenger train '%s' to be checked on %s." % (train.name, trainTimeCheck))

			except ValueError:
				try:
					self.scheduler.add_date_job(self.output, trainTime, args=[train], name=train.name)
					self.log("Schedule passenger train '%s' to be displayed on %s." % (train.name, trainTime))

				except ValueError:
					self.log("Passenger train '%s' (%s) already passed by." % (train.name, trainTime))

	def checkIfOnTime(self, remTrain):
		# return trains for station in question
		tReq = passenger.PassengerTrainRequest(PASSENGER_STATION_ID)
	 
		for train in tReq.getTrainList():
			if remTrain.name == train.name:
				trainTime = train.actualTime if (train.actualTime) else train.scheduledTime
				try:
					self.scheduler.add_date_job(self.output, trainTime, args=[train], name=train.name)
					self.log("Schedule passenger train '%s' to be displayed on %s." % (train.name, trainTime))

				except ValueError:
					self.log("Passenger train '%s' (%s) already passed by." % (train.name, trainTime))
				break


	def processFreight(self):
		# return trains for station in question
		freightTrains = freight.FreightTrainRequest(FREIGHT_STATION_ID)
 
		for train in freightTrains.getTrainList():
			# FIXME: only arrival atm
			if train.arrival > datetime.datetime.now():
				self.log("Schedule freight train '%s' to be displayed on %s." % (train.name, train.arrival))
				self.scheduler.add_date_job(self.output, train.arrival, args=[train], name=train.name)
			else:
				self.log("Freight train '%s' (%s) already passed." % (train.name, train.arrival))


	def processAutotrain(self):
		# return trains for station in question
		freightTrains = autotrain.AutoTrainRequest(AUTO_TRAIN_STATION_NAME)
	 
		for train in freightTrains.getTrainList():
			if train.arrival > datetime.datetime.now():
				self.log("Schedule auto train '%s' to be displayed on %s." % (train.name, train.arrival))
				self.scheduler.add_date_job(self.output, train.arrival, args=[train], name=train.name)
			else:
				self.log("Auto train '%s' (%s) already passed." % (train.name, train.arrival))

	def checkForDuplicates(self, event):
		jobs = self.scheduler.get_jobs()

		if jobs:
			dups = [job for job in jobs if job.name == event.job.name and job.next_run_time == event.job.next_run_time]
			if len(dups) > 1:
				self.log("Unscheduling %s." % event.job)
				self.scheduler.unschedule_job(event.job)


	def output(self, train):
		self.log("OUTPUT: %s" % train)
		f = open(OUTPUT_FILE, "a")
		f.write("\n%s" % train)
		f.close()


	def log(self, message):
		logging.info("* %s" % message)

		#fancyMessage = "[%s] %s" % (time.strftime("%d.%m.%Y %H:%M:%S"), message)
		
		#logfile = open("bahnanzeige.log", "a")
		#logfile.write("\n%s" % fancyMessage)
		#logfile.close()

def main():
	TrainScheduler()

if __name__ == '__main__':
	main()
