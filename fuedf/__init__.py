#!/usr/bin/python
#encoding: utf-8

import os

from flask import Flask
from flask import g
from flaskext.sqlalchemy import SQLAlchemy

# base directory
here = os.path.dirname(os.path.abspath(__file__))

# application setup
app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/fuedf.db' % here
#print app.config['SQLALCHEMY_DATABASE_URI']

def _jinja2_filter_datetime(date, fmt='%c'):
    return date.strftime(fmt)

app.jinja_env.filters['datetime'] = _jinja2_filter_datetime

# import models
from . import models

# import views
from . import views


@app.before_request
def before_request():
    g.rates = models.Rate.query.all()
    g._commit_requested = False

@app.teardown_request
def teardown_request(exception):
    if g._commit_requested:
        models.db.session.commit()

