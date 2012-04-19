#!/usr/bin/python
#encoding: utf-8

import os
import datetime
import types

from flask.ext.sqlalchemy import SQLAlchemy

from . import app

# Flask-SQLAlchemy setup
db = SQLAlchemy(app)

class Consumption(db.Model):
    __tablename__ = 'fuedf_consumption'
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    rate_id = db.Column(db.Integer, db.ForeignKey('fuedf_rate.rid'))
    rate = db.relationship('Rate', backref=db.backref('consumptions',
            lazy='dynamic'))
    value = db.Column(db.Integer, nullable=False)
    delta = db.Column(db.Integer, nullable=False)

    def __init__(self, date, rate, value, delta=0):
        if isinstance(date, types.StringTypes):
            date_ = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date_ = date
        self.date = date_
        self.rate_id = rate
        self.value = value
        self.delta = delta

    def __repr__(self):
        return '<Consumption %r@%r>' % (self.rate, self.date)

class Rate(db.Model):
    __tablename__ = 'fuedf_rate'
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    color = db.Column(db.String(7), nullable=False)

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return '<Rate %r(%r)' % (self.name, self.rid)

class User(db.Model):
    __tablename__ = 'fuedf_user'
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    login = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, email, login, password):
        self.name = name
        self.email = email
        self.login = login
        self.password = password

    def __repr__(self):
        return '<User %r(%r)' % (self.name, self.rid)


