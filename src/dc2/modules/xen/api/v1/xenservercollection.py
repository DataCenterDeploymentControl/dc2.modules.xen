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
except ImportError as e:
    raise(e)

# _hostentry_parser = RequestParser()
# _hostentry_parser.add_argument('hostname', type=str, required=True, location="json")
# _hostentry_parser.add_argument('ipaddress', type=str, required=True, location="json")
# _hostentry_parser.add_argument('ipnetwork', type=str, required=True, location="json")

class XenServerCollection(RestResource):

    def __init__(self, *args, **kwargs):
        super(XenServerCollection, self).__init__(*args, **kwargs)
        # self._ctl_hostentries = HostEntryController(DB.session)

    @needs_authentication
    @has_groups(['admin','users'])
    def get(self):
        xenserverlist = XenServer.query().all()
        if hostentrylist is not None:
            return [entry.to_dict for entry in hostentrylist], 200
        return [], 200

    @needs_authentication
    @has_groups(['admin','users'])
    def post(self):
        args = _hostentry_parser.parse_args()
        if g.auth_user is not None:
            try:
                hostentry, ipaddress = self._ctl_hostentries.new_with_ipaddress(hostname=args.hostname, ipaddress=args.ipaddress, ipnetwork=args.ipnetwork, username=g.auth_user)
                if hostentry is not None and ipaddress is not None:
                    return {
                        'hostname': hostentry.hostname,
                        'ipaddress': ipaddress.ipaddress
                    }, 200
            except Exception as e:
                app.logger.exception(msg="Exception occured")
                return {'error': True, 'message': lookup_error(error_code=e.orig.pgcode, format_entries=[e.orig.diag.message_primary])}, 400
        return {'error': True, 'message': 'Something went wrong'}, 400



