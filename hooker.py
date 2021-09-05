import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "lib"))    # for pyd
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "windll")) # for dll
print (os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "lib"))
