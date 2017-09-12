import os
import sys

if not "../tmpgen" in sys.path:
	sys.path.append("../tmpgen") 
if not 'templateGen' in sys.modules:
	templateGen = __import__('templateGen')
else:
	eval('import templateGen')
	templateGen = eval('reload(templateGen)')
	
import templateGen

try:
	from subprocess import call
except ImportError:
	print('import call failed.')
	
try:
	from subprocess import run
except ImportError:
	print('import run failed.')


def deploy():
	curdir = os.path.dirname(os.path.realpath(__file__))
	templateGen.analyseWithConfig(os.path.join(curdir,"config.ini"))
	command = "sudo apachectl restart"
	print("command:"+command)
	if sys.version_info < (3, 0):
		call(command, shell=True)
	else:
		run(command, shell=True)
	return


if __name__ == "__main__":
	deploy()