#!/bin/sh
HOST='ftp.users.qwest.net'
USER='yourid'
PASSWD='yourpw'
FILE='file.txt'

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
put $FILE
quit
END_SCRIPT
exit 0