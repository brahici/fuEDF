#!/usr/bin/python
#encoding: utf-8

import datetime

from flask import render_template, request, redirect, url_for, g, jsonify

from . import app
from .models import db, Consumption, Rate, User
import cache

DEFAULT_CHART_WEEKS_COUNT = 10

@app.route('/', methods=['GET', ])
@cache.cached('view')
def index():
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        return redirect(url_for('index'))
    entries = Consumption.query.order_by('date desc').paginate(
            page, 6, error_out=False)
    total = sum([cons.delta for cons in entries.items])
    return render_template('root.jj', entries=entries, total=total)

@app.route('/cons/add', methods=['POST', 'GET'])
def consumption_add():
    if request.method == 'GET':
        return render_template('edit_cons.jj', server_method='consumption_add',
                values={}, error='')
    else:
        #TODO: improve values checks
        _f = request.form
        if (_f['date'].strip() and _f['value'].strip() and
                _f['rate'].strip()):
            date_ = _f['date'].strip()
            rate_ = _f['rate'].strip()
            value_ = int(_f['value'].strip())
            delta_ = 0
            prev_cons = Consumption.query.filter(Consumption.date < date_ and \
                    Consumption.rate_id == rate_).order_by('date desc').first()
            if prev_cons:
                delta_ = value_ - prev_cons.value
            _rate = Consumption(date_, rate_, value_, delta_)
            db.session.add(_rate)
            g._commit_requested = True
            cache.cached.clear()
            return redirect(url_for('consumption_add'))
        values = {
            'date': _f['date'],
            'value': _f['value'],
            'rate': _f['rate'],
        }
        error = 'A value is missing'
        return render_template('edit_cons.jj', error=error,
                server_method='consumption_add', values=values)

@app.route('/cons/<int:rate_rid>')
@cache.cached('view')
def get_rates_cons(rate_rid):
    entries = Consumption.query.filter(Consumption.rate_id == rate_rid)\
            .order_by('date desc').all()
    total = sum([cons.delta for cons in entries])
    return render_template('cons.jj', entries=entries, total=total)

# no need to cache this one
# g.rates is set with a cached function
@app.route('/_get_rates')
def get_rates():
    rates_ = []
    for rate in g.rates:
        rates_.append((rate['name'], rate['rid']))
    return jsonify(rates=dict(rates_))

@app.route('/charts')
@cache.cached('view')
def consumption_charts():
    dates = [cons.date.strftime('%Y-%m-%d')
            for cons in Consumption.query.distinct(Consumption.date) \
                    .group_by(Consumption.date) \
                    .order_by(Consumption.date).all()]
    start_date = len(dates) > DEFAULT_CHART_WEEKS_COUNT and \
            dates[-DEFAULT_CHART_WEEKS_COUNT] or dates[0]
    end_date = dates[-1]
    return render_template('cons_charts.jj', dates=dates,
            start_date=start_date, end_date=end_date)

_DATA_CHART_MODES = ['values', 'progressive', 'total', 'global', ]

@app.route('/_get_charts_data')
@cache.cached('view')
def _get_charts_data():
    mode = request.args.get('mode', 'values')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if mode not in _DATA_CHART_MODES:
        mode = 'values'
    if start_date and end_date and start_date != end_date:
        # swap dates if start is after end
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        entries = Consumption.query.filter(Consumption.date>=start_date) \
                    .filter(Consumption.date<=end_date).all()
    elif start_date and not end_date:
        entries = Consumption.query.filter(Consumption.date>=start_date).all()
    elif end_date and not start_date:
        entries = Consumption.query.filter(Consumption.date<=end_date).all()
    else:
        entries = Consumption.query.all()
    values = {}
    dates = []
    rates = []
    colors = []
    if mode == 'global':
        rates = ['Global', ]
        values = {'Global': []}
        colors = []
        _values = values['Global']
        cur_date = ''
        date_cons = 0
        for entry in entries:
            fmt_date = entry.date.strftime('%Y-%m-%d')
            if fmt_date not in dates:
                dates.append(fmt_date)
            if cur_date == fmt_date:
                date_cons += entry.delta
            else:
                if cur_date:
                    _values.append(date_cons)
                cur_date = fmt_date
                date_cons = entry.delta
        if cur_date:
            _values.append(date_cons)
    else:
        for entry in entries:
            fmt_date = entry.date.strftime('%Y-%m-%d')
            rate = entry.rate.name
            if fmt_date not in dates:
                dates.append(fmt_date)
            if rate not in rates:
                rates.append(rate)
                colors.append(entry.rate.color)
            _values = values.setdefault(rate, [])
            if _values and mode == 'progressive':
                _values.append(_values[-1] + entry.delta)
            elif mode == 'total':
                _values.append(entry.value)
            else:
                _values.append(entry.delta)
    return jsonify(dates=dates, values=values, rates=rates, colors=colors)

