#!/usr/bin/python
#encoding: utf-8

import sys
import fuedf

if len(sys.argv) == 2 and sys.argv[1] == 'initdb':
    _db = fuedf.models.db
    _User = fuedf.models.User
    _Rate = fuedf.models.Rate
    _db.create_all()
    updated = False
    if not _User.query.filter_by(login='admin').all():
        user = _User('Administrator', 'brahici@altern.org', 'admin', 'AAA')
        _db.session.add(user)
        updated = True

    for rate_name, rate_color in (
            ('BleuCreuses', '#0000ff'), ('BleuPleines', '#0000ff'),
            ('BlancCreuses', '#000000'), ('BlancPleines', '#000000'),
            ('RougeCreuses', '#ff0000'), ('RougePleines', '#ff0000')):
        if not _Rate.query.filter_by(name=rate_name).all():
            rate = _Rate(rate_name, rate_color)
            _db.session.add(rate)
            updated = True
    if updated:
        _db.session.commit()
else:
    fuedf.app.run(debug=True)
