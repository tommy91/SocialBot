#!/bin/sh

# To change
HOST='FTP.USERS.QWEST.NET'
USER='YOUR_USER'
PASSWD='YOUR_PASSWORD'
BASEDIR='BASE_DIRECTORY'


FTP_ERROR_MSG="Can't change directory to"
FTP_TRASFERRED_MSG="File successfully transferred"
FTP_CREATED_MSG="The directory was successfully created"


function ftpCheckDirExists {
  ftp -n $HOST <<END_SCRIPT 
  quote USER $USER
  quote PASS $PASSWD
  cd $BASEDIR/$1
  quit 
END_SCRIPT
}

function ftpMakeDir {
  ftp -n -v $HOST <<END_SCRIPT
  quote USER $USER
  quote PASS $PASSWD
  mkdir $BASEDIR/$1
  quit 
END_SCRIPT
}

function ftpMPut {
  ftp -n -v $HOST <<END_SCRIPT
  quote USER $USER
  quote PASS $PASSWD
  cd $BASEDIR/$3
  prompt off
  lcd $1
  mput *
  quit 
END_SCRIPT
}

function ftpPut {
  ftp -n -v $HOST <<END_SCRIPT
  quote USER $USER
  quote PASS $PASSWD
  cd $BASEDIR/$3
  prompt off
  lcd $1
  put $2
  quit 
END_SCRIPT
}

function cutPath {
  return $(echo "$1" | cut -d/ -f 2-)
}

function explore {
  if $2; then 
    p=$(cutPath $1)
    if ftpCheckDirExists $p | grep -q "$FTP_ERROR_MSG"; then
      echo "$p -> NOT found!"
      if ftpMakeDir $p | grep -q "$FTP_CREATED_MSG"; then
        echo "$p -> Created."
      else
        echo "$p -> Error!"
        exit 1
      fi
    else
      echo "$p -> Ok."
    fi
  fi
  for file in "$1"/*
    do
      if [ -f "$file" ]; then
        filename=$(basename "$file")
        p=$(cutPath $1)
        if ftpPut $1 $filename $p | grep -q "$FTP_TRASFERRED_MSG"; then
          echo "$file -> Ok."
        else
          echo "$file -> Error!"
          exit 1
        fi
      fi
    done
  for file in "$1"/*
    do
      if [ -d "$file" ]; then
        explore $file true
      fi
    done
}

function ftp_upload {
  echo "\nUploading via ftp"
  echo "  from: '$1'"
  echo "  to: '$BASEDIR'"
  echo "\nBegin upload:"
  explore $1 $2
  echo "End upload.\n"
}

ftp_upload 'my_site' false

