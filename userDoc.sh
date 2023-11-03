#!/bin/bash
#This script sets up the basic configuration to launch the script
#And to use the webdav protocol
#python3 and davfs2 are needed 
#The user is asked to enter credentials of a chosen cloud service that supports webdav
#The user will need a username and a password for the cloud service account
#A crontab file is created to automate the launch of the script  
#First  install python 3 and devafs2
directory=`pwd`
user=`whoami`
uid=`id -u $user`
gid=`id -g $user`
echo "Installing python"
sudo apt-get install -i python3
echo "Installing davfs2"
sudo apt-get install -i davfs2
sudo mkdir -p /mnt/dav
echo "Enter cloud service URL"
read URL
echo "Enter username for cloud account"
read username
echo "Enter password"
read password 
echo "Beginning configuration" 
fstabLine="$URL  /mnt/dav davfs _netdev,noauto,user,uid=$uid,gid=$gid 0 0"
echo "$fstabLine" >> /etc/fstab 
davSecrets="$URL $username $password"
echo "$davSecrets" >> /etc/davfs2/secrets
sudo usermod -a -G davfs2 $user
echo "Starting mount" 
sudo mount /mnt/dav
echo "Mount successful"
#Setting rights on all the project files
#The scripts files should be executable 
sudo find . -type f -iname "*.py" -exec chmod 511 {} \;
# Config file has all rights 
sudo find . -type f -iname "config.yaml" -exec chmod 777 {} \;
# Log file has read only rights, won't need to be executed or written in 
sudo find . -type f -iname "log.log" -exec chmod 444 {} \;

# Automate script execution
# Configure crontab to call projet.py and launch the archive of the file 
# Each day at 1 am, every day, every month, every day of the week 
# execute projet.py
{ crontab -l -u $user; echo "0 1 * * * cd $directory; python3 backup.py"; } | crontab -u $user -

# Check crontab was created.
if sudo test -f "/var/spool/cron/crontabs/$user"
then
	echo "Crontab file created successfully"
	# Launch cron service
	sudo service cron start
else
	echo "Error: Cron file was not created."
fi


