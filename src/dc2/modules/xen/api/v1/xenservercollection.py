# -*- coding: utf-8 -*-
#
#
# (DC)² - DataCenter Deployment Control
# Copyright (C) 2010, 2011, 2012, 2013, 2014  Stephan Adig <sh@sourcecode.de>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__ = 'stephan.adig'

try:
    from flask_restful import Resource as RestResource
    from flask_restful.reqparse import RequestParser
    from flask import g, request
except ImportError as e:
    raise e


try:
    from dc2.core.application import app
    from dc2.core.database import DB
    from dc2.core.database.errors import lookup_error
    from dc2.core.helpers import hash_generator
    from dc2.core.auth.decorators import needs_authentication, has_groups
except ImportError as e:
    raise e

try:
    from ...db.models import XenServer
    from dc2.core.modules.usersgroups.db.models import User
except ImportError as e:
    raise(e)

_xenserver_parser = RequestParser()
_xenserver_parser.add_argument('title', dest='title', type=str, required=True, location='json')
_xenserver_parser.add_argument('hostname', dest='hostname', type=str, required=True, location='json')
_xenserver_parser.add_argument('port', dest='port', type=int, required=True, location='json')
_xenserver_parser.add_argument('username', dest='username', type=str, required=True, location='json')
_xenserver_parser.add_argument('password', dest='password', default=None, type=str, required=False, location='json')

class XenServerCollection(RestResource):

    def __init__(self, *args, **kwargs):
        super(XenServerCollection, self).__init__(*args, **kwargs)
        # self._ctl_hostentries = HostEntryController(DB.session)

    @needs_authentication
    @has_groups(['admin'])
    def get(self):
        try:
            xenserverlist = XenServer.query.all()
            if xenserverlist is not None:
                return [entry.to_dict for entry in xenserverlist], 200
        except Exception as e:
            app.logger.exception(msg='Exception occured')
            return None, 404

    @needs_authentication
    @has_groups(['admin'])
    def post(self):
        args = _xenserver_parser.parse_args()
        if g.auth_user is not None:
            try:
                user = User.query.filter_by(username=g.auth_user).first()
                xen_rec = XenServer()
                xen_rec.title = args.title
                xen_rec.hostname = args.hostname
                xen_rec.port = args.port
                xen_rec.username = args.username
                xen_rec.password = args.password
                xen_rec.created_by = user
                DB.session.add(xen_rec)
                DB.session.commit()
                print(xen_rec.to_dict)
                return xen_rec.to_dict, 200
            except Exception as e:
                app.logger.exception(msg="Exception occured")
                return {'error': True, 'message': "An Error Occured"}, 400


class XenServerEntries(RestResource):
    def __init__(self, *args, **kwargs):
        super(XenServerEntries, self).__init__(*args, **kwargs)

    @needs_authentication
    @has_groups(['admin'])
    def put(self, id=None):
        try:
            if g.auth_user is not None and id is not None:
                args = _xenserver_parser.parse_args()
                user = User.query.filter_by(username=g.auth_user).first()
                entry = XenServer.query.filter_by(id=id).first()
                print(entry.to_dict)
                entry.title = args.title
                entry.hostname = args.hostname
                entry.port = args.port
                entry.username = args.username
                entry.password = args.password
                entry.updated_by = user
                DB.session.commit()
                return entry.to_dict, 200
            else:
                return {'error': True, 'message': 'No ID given'}, 400
        except Exception as e:
            app.logger.exception(msg='An Exception Occured')
            return {'error': True, 'message': 'An Error Occured'}, 400

    @needs_authentication
    @has_groups(['admin'])
    def get(self, id=None):
        try:
            entry = XenServer.query.filter_by(id=id).first()
            return entry.to_dict, 200
        except Exception as e:
            app.logger.exception(msg="An Exception Occured")
            return {'error': True, 'message': 'An Error Occured'}, 400

    @needs_authentication
    @has_groups(['admin'])
    def delete(self, id=None):
        try:
            if id is not None:
                entry = XenServer.query.filter_by(id=id).first()
                DB.session.delete(entry)
                DB.session.commit()
                return {'error': False, 'message': 'Entry deleted'}, 200
            else:
                return {'error': True, 'message': 'No ID Given'}, 400
        except Exception as e:
            app.logger.exception(msg="Exception occured")
            return {'error': True, 'message': "An Error Occured"}, 400
