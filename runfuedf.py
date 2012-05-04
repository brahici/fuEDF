#!/usr/bin/python
#encoding: utf-8

import sys
import fuedf

if len(sys.argv) == 2 and sys.argv[1] == 'initdb':
    fuedf.initdb()
else:
    fuedf.app.run(debug=True)
