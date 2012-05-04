fuEDF
=====

fuEDF is a small web application for following my energy consumptions (EDF
Tempo contract).

It's powered by Flask. Data persists in a sqlite3 database, handled through
Flask-Alchemy.

It requires some javascript libraries:

- jQuery for ajax calls
- Highcharts for chart rendering
- momentjs for date handling


Licence
-------

fuEDF is released under BSD licence. See LICENCE.


Important
---------

There's no form nor view for updating/deleting consumptions. Avoid to update
consumption values directly in database, it may lead to data inconsistencies.
The same applies about deleting.
Having a function that update deltas after insert, update or delete is in my
TODO list.

The form for adding new values is pretty tacky. I personnally use a script
for adding new values (using Kenneth Reitz's Requests fantastic module).


Installation
------------

I recommand to use a virtual environment with virtualenvwrapper:
http://www.doughellmann.com/projects/virtualenvwrapper/

Use pip-requirements.txt for installing Python dependencies.

Please note that BeautifulSoup4 is required for the tests suite, but is not
in the requirements.

For the javascript libraries, jQuery is loaded from ajax.googleapis.com. You
have to manually download and install Highcharts and momentjs.

- http://www.highcharts.com
- http://momentjs.com

These libraries has to be installed in fuedf/static/js/ (works fine with
symbolic links).

To initialize the database (structure + Tempo rates)::

    $ python runfuedf.py initdb


Running
-------

You can run fuEDF as standalone web server or through a WSGI server.

Standalone::

    $ python runfuedf.py

WSGI server (e.g. gunicorn)::

    $ gunicorn -w1 -b:5000 fuedf:app

