#!/usr/bin/python
#encoding: utf-8

from flask import render_template, request, redirect, url_for, g, jsonify

from . import app
from .models import db, Consumption, Rate, User

@app.route('/', methods=['GET', ])
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
            return redirect(url_for('consumption_add'))
            return 'OK'
        values = {
            'date': _f['date'],
            'value': _f['value'],
            'rate': int(_f['rate']),
        }
        error = 'A value is missing'
        return render_template('edit_cons.jj', error=error,
                server_method='consumption_add', values=values)

@app.route('/_get_rates')
def get_rates():
    rates_ = []
    for rate in g.rates:
        rates_.append((rate.name, rate.rid))
    return jsonify(rates=dict(rates_))

