import yaml
import logging
from BackupUtilities import *
from emailing import *

logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO, format='%(levelname)s:%(asctime)s:%(message)s')

# Readinfg the yaml configuration file
def read_yaml(file_path):
	with open(file_path,"r") as f:
		return yaml.safe_load(f)
	
#Getting all variables from the yaml file 
CONFIG=read_yaml("./config.yaml")



#Link stores the zip file link
LINK=CONFIG['LINK']
if LINK is None:
	logging.error(' No link was specified in the configuration file')
	exit()


#Duration of conservation of the file on the server
DURATION=CONFIG['DURATION']
if DURATION is None:
	logging.info(' No duration was specified, default duration is used : 1')
	DURATION=1


#Duration type of conservation of the file on the server
DURATIONTYPE=CONFIG['DURATIONTYPE']
if DURATIONTYPE is None:
	logging.info(' No duration type was specified, default duration is used : days')
	DURATIONTYPE="days"
NOTIFY=CONFIG['NOTIFY']


#check if there are specified receivers for the notification
SMTP_MAIL_RECEIVERS=CONFIG['SMTP_MAIL_RECEIVERS']
if SMTP_MAIL_RECEIVERS is None:
	logging.info(' No webhook was specified, notoification flag is set to false')
	NOTIFY=False



logging.info(' Retrieved information successfully from configuration file')
manageFile(DURATION,DURATIONTYPE,NOTIFY)
fileLink=getFileLink(LINK,NOTIFY)
SQL_FILE=extractFile(fileLink,NOTIFY)

archiveFile(SQL_FILE,NOTIFY)
manageFile(DURATION,DURATIONTYPE,NOTIFY)