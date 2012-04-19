#!/usr/bin/python
#encoding: utf-8

import os
from types import StringTypes
import datetime

from flask import Flask
from flask import g
from flask.ext.sqlalchemy import SQLAlchemy

# base directory
here = os.path.dirname(os.path.abspath(__file__))

# application setup
app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/fuedf.db' % here
#print app.config['SQLALCHEMY_DATABASE_URI']

def _jinja2_filter_datetime(date, fmt='%c'):
    if isinstance(date, StringTypes):
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except Exception, e:
            print(e)
            return date
    return date.strftime(fmt)

def _jinja2_filter_reversed(iterable):
    return reversed(iterable)

app.jinja_env.filters['datetime'] = _jinja2_filter_datetime
app.jinja_env.filters['reversed'] = _jinja2_filter_reversed

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

def initdb():
    _db = models.db
    _User = models.User
    _Rate = models.Rate
    _db.create_all()
    updated = False
    if not _User.query.filter_by(login='admin').all():
        user = _User('Administrator', 'brahici@altern.org', 'admin', 'AAA')
        _db.session.add(user)
        updated = True

    for rate_name, rate_color in (
            ('BleuCreuses', '#4572a7'), ('BleuPleines', '#4572a7'),
            ('BlancCreuses', '#b6b6b6'), ('BlancPleines', '#b6b6b6'),
            ('RougeCreuses', '#aa4643'), ('RougePleines', '#aa4643')):
        if not _Rate.query.filter_by(name=rate_name).all():
            rate = _Rate(rate_name, rate_color)
            _db.session.add(rate)
            updated = True
    if updated:
        _db.session.commit()

