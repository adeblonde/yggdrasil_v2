from yggdrasil.yggdrasil import run
import sys

if __name__ == "__main__" :
	no_backend = False
	if sys.argv[11] == "True" :
		no_backend = True
	if sys.argv[9] == 'X' :
		run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], None, sys.argv[10], no_backend)
	else :
		run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], no_backend)