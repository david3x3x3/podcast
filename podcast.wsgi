#!/usr/bin/python3
appdir = '.'
activator = appdir + '/venv/bin/activate_this.py'
with open(activator) as f:
           exec(f.read(), {'__file__': activator})

import sys

sys.path.insert(0, appdir)

from application import application

if __name__ == '__main__':
       application.run()
