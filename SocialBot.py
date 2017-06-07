import os
import sys

from SBProg import SBProg


def removeFilesByExtension(ext):
	filelist = [ f for f in os.listdir(".") if f.endswith(ext) ]
	for f in filelist:
		os.remove(f)


def clean():
	sys.stdout.write("\nCleaning up directory:\n")
	sys.stdout.flush()
	sys.stdout.write("\n    files .pyc -> ")
	sys.stdout.flush()
	removeFilesByExtension('.pyc')
	sys.stdout.write("ok.\n")
	sys.stdout.flush()
	sys.stdout.write("    database -> ")
	sys.stdout.flush()
	removeFilesByExtension('.db')
	sys.stdout.write("ok.\n")
	sys.stdout.flush()
	sys.stdout.write("\nCleaning up complete.\n\nExit. Bye!\n\n")
	sys.stdout.flush()
	sys.exit(0)


if __name__ == '__main__':
	lp = len(sys.argv)
	if lp > 2:
		print("\n\tError: " + str(lp-1) + " params, admitted only 1! Ignored all.\n")
	elif lp > 1:
		if(sys.argv[1]=='-clean'):
			clean()
		if(sys.argv[1]=='-f'):
			print("\n\tFast Mode On.\n\tNo sleep char/line.\n")
			SBProg(sleepChar=0.0, sleepLine=0.0).runProgram()
		elif(sys.argv[1]=='-t'):
			print("\n\tTest Mode On.\n")
			SBProg(isTest=True).runProgram()
		elif(sys.argv[1] in ['-ft','-tf']):
			print("\n\tFast Mode On.\n\tNo sleep char/line.\n\n\tTest Mode On.\n")
			SBProg(isTest=True, sleepChar=0.0, sleepLine=0.0).runProgram()
		else:
			print("\n\tError: unknown command '" + sys.argv[1] + "', ignored.\n")
			SBProg().runProgram()
	else:
		SBProg().runProgram()

