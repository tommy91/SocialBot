#!/bin/bash

# for Mac use: 		brew install lftp
# for Ubuntu use: 	sudo apt-get install lftp

TARGET='BASE_DIRECTORY'
SOURCE='my_site'
TRAGET_LOG='/BASE_DIRECTORY'
FILE_LOG='log.log'
FILE_LOG_ESCAPED="log.log"
SOURCE_LOG='logs/'

GET_OK_MSG='File successfully transferred'

HOSTNAME='FTP.USERS.QWEST.NET'
USERNAME='YOUR_USER'
PASSWORD='YOUR_PASSWORD'
LOCALSOURCE=''

function ftpGet {
	ftp -n -v $HOSTNAME <<END_SCRIPT
	quote USER $USERNAME
	quote PASS $PASSWORD
	cd $TRAGET_LOG
	prompt off
	get $FILE_LOG "$SOURCE_LOG$(date +"%Y%m%d%H%M").log"
	quit 
END_SCRIPT
}

function ftpls {
	ftp -n -v $HOSTNAME <<END_SCRIPT
	quote USER $USERNAME
	quote PASS $PASSWORD
	cd $TRAGET_LOG
	ls
	quit 
END_SCRIPT
}

function lftpSynch {
	changePermissions
	echo "Updating files on remote server.. "
	lftp -f "
	open $HOSTNAME
	user $USERNAME $PASSWORD
	set ftp:ssl-allow no
	set net:reconnect-interval-base 1
	mirror -R --recursion=always --delete --verbose $SOURCE $TARGET
	chmod -R 0775 $TARGET
	bye
	"
	printf "Done.\n\n"
}

function checkLocalDir {
	printf "Check if logs directory exists.. "
	if [ -d "$SOURCE_LOG" ]; then
		echo "ok"
	else
		printf "doesn't exists.. "
		mkdir $SOURCE_LOG
		echo "created!"
	fi
}

function synchData {
	echo "Get server log before update.. "
	checkLocalDir
	printf "Check if log file exists.. "
	if ftpls | grep $FILE_LOG_ESCAPED; then
		echo "here it is :)"
		printf "Download log.. "
		if ftpGet | grep -q "$GET_OK_MSG"; then
			printf "Done.\n\n"
		else
			echo "Error!"
			printf "Exit whitout synch!\n\n"
			return
		fi
	else
		printf "doesn't exist!\n\n"
	fi
	lftpSynch
}

function changePermissions {
	printf "Change all folder permissions.. "
	chmod -R 755 $SOURCE
	printf "ok\n\n"
}

printf "\nHi Uploader!\n\n"
synchData
printf "Bye!\n\n"
