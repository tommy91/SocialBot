import os
import sys

from SBProg import SBProg
from Utils import write


def removeFilesByExtension(ext):
	filelist = [ f for f in os.listdir(".") if f.endswith(ext) ]
	for f in filelist:
		os.remove(f)


def clean():
	write("\nCleaning up directory:\n")
	write("\n    files .pyc -> ")
	removeFilesByExtension('.pyc')
	write("ok.\n")
	write("    database -> ")
	removeFilesByExtension('.db')
	write("ok.\n")
	write("\nCleaning up complete.\n\nExit. Bye!\n\n")
	sys.exit(0)


if __name__ == '__main__':
	lp = len(sys.argv)
	if lp > 2:
		print("\n\tError: " + str(lp-1) + " params, admitted only 1! Ignored all.\n")
	elif lp > 1:
		if(sys.argv[1]=='-clean'):
			clean()
		elif(sys.argv[1]=='-t'):
			print("\n\tTest Mode On.\n")
			SBProg(isTest=True).runProgram()
		else:
			print("\n\tError: unknown command '" + sys.argv[1] + "', ignored.\n")
			SBProg().runProgram()
	else:
		SBProg().runProgram()

