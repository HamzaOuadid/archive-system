import requests
import zipfile
import io
import tarfile
import datetime
import os
import time
import logging
from emailing import buildPayload
from emailing import sendEmail
import shutil
import hashlib
import glob
import yaml



#defining syntax for log file 
logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO, format='%(levelname)s:%(asctime)s:%(message)s')

def read_yaml(file_path):
	with open(file_path,"r") as f:
		return yaml.safe_load(f)

#Getting all variables from the yaml file
CONFIG=read_yaml("./config.yaml")


               


def getFileLink(LINK, NOTIFY):

    try:
        logging.info('Trying to connect...')
        fileLink = requests.get(LINK)
        logging.info('Connection successful')
        if NOTIFY:
            message = buildPayload('File retrieval', 'Done')
            subject = 'File Retrieval Notification'
            sender_email = CONFIG['SMTP_MAIL_SENDER']
            recipient_email = CONFIG['SMTP_MAIL_RECEIVERS']
            smtp_server = CONFIG['SMTP_SERVER']
            smtp_port = CONFIG['SMTP_PORT']
            smtp_password = CONFIG['SMTP_PASSWORD']
            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)
        return fileLink
    except requests.exceptions.RequestException as e:
        logging.error(e.strerror)
        if NOTIFY:
            message = buildPayload('File retrieval', 'ERROR, review log')
            subject = 'File Retrieval Notification'
            sender_email = CONFIG['SMTP_MAIL_SENDER']
            recipient_email = CONFIG['SMTP_MAIL_RECEIVERS']
            smtp_server = CONFIG['SMTP_SERVER']
            smtp_port = CONFIG['SMTP_PORT']
            smtp_password = CONFIG['SMTP_PASSWORD']
            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)

               



def extractFile(fileLink, NOTIFY):
    
    z = zipfile.ZipFile(io.BytesIO(fileLink.content))
    now = datetime.datetime.now()
    name = now.strftime("%Y%d%m")
    pathFolder = "./" + name + "/"
    
    if os.path.exists(pathFolder):
        logging.info('AN ARCHIVED FOR THIS FILE ALREADY EXISTS, NO FILE CREATED')
        SQL_FILE = None
    else:
        z.extractall(path=pathFolder)
        SQL_FILE = z.infolist()[0].filename
        logging.info('EXTRACTION SUCCESSFUL: filename ' + SQL_FILE)

        extracted_hash = hashlib.sha256(open(pathFolder + SQL_FILE, 'rb').read()).hexdigest()
        latest_backup_file = max(glob.glob("/mnt/dav/????????????.tgz"))

        if os.path.exists(latest_backup_file):
            latest_backup_hash = hashlib.sha256(open(latest_backup_file, 'rb').read()).hexdigest()

            if extracted_hash == latest_backup_hash:
                logging.info('Hash of the extracted file matches the latest backup.')
                SQL_FILE = None

        if NOTIFY:
            message = buildPayload('File extraction', 'Done')
            subject = 'File Extraction Notification'
            sender_email = CONFIG['SMTP_MAIL_SENDER']
            recipient_email = CONFIG['SMTP_MAIL_RECEIVERS']
            smtp_server = CONFIG['SMTP_SERVER']
            smtp_port = CONFIG['SMTP_PORT']
            smtp_password = CONFIG['SMTP_PASSWORD']
            
            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)

    return SQL_FILE



def archiveFile(SQL_FILE, NOTIFY):
    if SQL_FILE is None:
        print("Empty")
    else:
        logging.info('ARCHIVING FILE')
        now = datetime.datetime.now()
        name = now.strftime("%Y%d%m")
        logging.info("The archive name" + name)
        archiveName = "/mnt/dav/" + name + ".tgz"
        
        # Check if there is a prior version of the file
        latest_backup_files = glob.glob("/mnt/dav/????????????.tgz")
        if not latest_backup_files:
            logging.info('No prior version found. Archiving directly without hash check.')
            file_obj = tarfile.open(archiveName, "w")
            file_obj.add("./" + name + "/" + SQL_FILE)
            file_obj.close()
        else:
            # Calculate the hash of the current file
            with open("./" + name + "/" + SQL_FILE, 'rb') as f:
                current_file_contents = f.read()
                current_file_hash = hashlib.sha256(current_file_contents).hexdigest()
            
            # Calculate the hash of the latest backup file
            with open(latest_backup_files[0], 'rb') as f:
                latest_backup_contents = f.read()
                latest_backup_hash = hashlib.sha256(latest_backup_contents).hexdigest()
            
            if current_file_hash == latest_backup_hash:
                logging.info('Hashes match. Skipping archiving.')
            else:
                logging.info('Hashes do not match. Proceeding with archiving.')
                file_obj = tarfile.open(archiveName, "w")
                file_obj.add("./" + name + "/" + SQL_FILE)
                file_obj.close()

        logging.info('ARCHIVE SUCCESSFUL')

        # Update latest backup
        latest_backup_file = max(glob.glob("/mnt/dav/????????????.tgz"))  # Find the latest backup file
        shutil.copy(archiveName, latest_backup_file)

        shutil.rmtree("./" + name, ignore_errors=True)

        if NOTIFY:
            message = buildPayload('File archive', 'Done')
            subject = 'File Archive Notification'
            sender_email = CONFIG['sender_email']
            recipient_email = CONFIG['recipient_email']
            smtp_server = CONFIG['smtp_server']
            smtp_port = CONFIG['smtp_port']
            smtp_password = CONFIG['smtp_password']
            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)


            







def manageFile(Duration, durationType, NOTIFY):
    print("looking for files")
    files = os.listdir("/mnt/dav/")
    for f in files:
        if f.endswith('.tgz'):
            print(f)
            try:
                dateCreation = datetime.datetime.strptime(time.ctime(os.path.getctime("/mnt/dav/" + f)), "%c")
                now = datetime.datetime.now()
                # Compare the date of creation of the archive with the duration from configuration file
                if dateCreation + datetime.timedelta(**{durationType: Duration}) < now:
                    print("should be deleted")
                    print("-----------------")
                    try:
                        os.remove("/mnt/dav/" + f)
                        logging.info('FILES EXCEEDING DURATION DELETED')
                        if NOTIFY:
                            message = buildPayload('Files management', 'Done')
                            subject = 'Files Management Notification'
                            sender_email = CONFIG['sender_email']
                            recipient_email = CONFIG['recipient_email']
                            smtp_server = CONFIG['smtp_server']
                            smtp_port = CONFIG['smtp_port']
                            smtp_password = CONFIG['smtp_password']
                            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)
                    except OSError as e:
                        logging.error(e.strerror)
                        if NOTIFY:
                            message = buildPayload('Files management', 'ERROR, review log')
                            subject = 'Files Management Notification'
                            sender_email = CONFIG['sender_email']
                            recipient_email = CONFIG['recipient_email']
                            smtp_server = CONFIG['smtp_server']
                            smtp_port = CONFIG['smtp_port']
                            smtp_password = CONFIG['smtp_password']
                            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)

            except OSError:
                logging.error("Path does not exist")
                if NOTIFY:
                    message = buildPayload('File management', 'ERROR, review log')
                    subject = 'Files Management Notification'
                    sender_email = CONFIG['sender_email']
                    recipient_email = CONFIG['recipient_email']
                    smtp_server = CONFIG['smtp_server']
                    smtp_port = CONFIG['smtp_port']
                    smtp_password = CONFIG['smtp_password']
                    sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)
                    
