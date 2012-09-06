
fuEDF
=====

fuEDF is a small web application for following my energy consumptions (EDF
Tempo contract).

It's powered by Flask. Data persists in a sqlite3 database, handled through
Flask-Alchemy.

fuEDF uses some javascript libraries:

- jQuery for ajax calls (http://jquery.com)
- Highcharts for chart rendering (http://www.highcharts.com)
- momentjs for date handling (http://momentjs.com)
- spin.js for spinner (http://fgnass.github.com/spin.js/)


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

Install fuEDF and dependencies::

    $ python setup.py install

fuEDF is shipped with momentjs, spin.js and Highcharts. jQuery is loaded from
ajax.googleapis.com.

**Be aware that Highcharts is not free for commercial use**. See
http://shop.highsoft.com/highcharts.html for details.

You can perform unitests by running directly fuedf_test.py. You may want to
run tests with nosetests, as it will also perform a coverage measure::

    $ python setup.py nosetests

You can view coverage HTML report directly in fuEDF if you reinstall fuEDF
after running nosetests (a link will appear in application root view).

To initialize the database (structure + Tempo rates)::

    $ runfuedf.py initdb


Running
-------

You can run fuEDF as standalone web server or through a WSGI server.

Standalone::

    $ runfuedf.py

WSGI server (e.g. gunicorn)::

    $ gunicorn -w1 -b:5000 fuedf:app

