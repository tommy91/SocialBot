import os
import sys

import SBProg
import Utils


def removeFilesByExtension(ext):
	filelist = [ f for f in os.listdir(".") if f.endswith(ext) ]
	for f in filelist:
		os.remove(f)


def clean():
	print "\nCleaning up directory:"
	sys.stdout.write("\n    files .pyc -> ")
	sys.stdout.flush()
	removeFilesByExtension('.pyc')
	print "ok."
	sys.stdout.write("    database -> ")
	sys.stdout.flush()
	removeFilesByExtension('.db')
	print "ok."
	print "\nCleaning up complete.\n\nExit. Bye!\n"
	sys.exit(0)


if __name__ == '__main__':
	lp = len(sys.argv)
	if lp > 2:
		print "\n\tError: " + str(lp-1) + " params, admitted only 1! Ignored all.\n"
	elif lp == 2:
		if sys.argv[1] == '-clean':
			clean()
		elif sys.argv[1] == '-t':
			print "\n\tTest Mode On.\n"
			SBProg.SBProg(isTest=True).runProgram()
		else:
			print "\n\tError: unknown command '" + sys.argv[1] + "', ignored.\n"
			SBProg.SBProg().runProgram()
	else:
		SBProg.SBProg().runProgram()

