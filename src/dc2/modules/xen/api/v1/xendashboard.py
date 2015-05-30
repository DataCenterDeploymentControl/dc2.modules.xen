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

try:
    from dc2.xen.lib import XApi
except ImportError as e:
    raise(e)


class XenCollection(RestResource):

    def __init__(self, *args, **kwargs):
        super(XenCollection, self).__init__(*args, **kwargs)
        # self._ctl_hostentries = HostEntryController(DB.session)

    @needs_authentication
    @has_groups(['users', 'admin'])
    def get(self):
        try:
            xenserverlist = XenServer.query.all()
            if xenserverlist is not None:
                return [entry.to_dict for entry in xenserverlist], 200
        except Exception as e:
            app.logger.exception(msg='Exception occured')
            return None, 404

class XenServerData(RestResource):
    def __init__(self, *args, **kwargs):
        super(XenServerData, self).__init__(*args, **kwargs)

    @needs_authentication
    @has_groups(['users', 'admin'])
    def get(self, id=None):
        try:
            if id is not None:
                entry = XenServer.query.filter_by(id=id).first()
                print(entry.to_dict)
                xen_conn = XApi("http://{0}:{1}".format(entry.hostname, entry.port))
                xen_conn.login(entry.username, entry.password)
                xen_host_data = {
                    'host': [],
                    'vms': []
                }
                xen_host_list = xen_conn.HOSTS.list_hosts()
                xen_vm_list = xen_conn.VMS.list_vms()
                for host_uuid in xen_host_list:
                    host = xen_conn.HOSTS.get_host(host_uuid)
                    xen_host_data['host'].append({
                        'xen_hostname': host.name_label,
                        'xen_no_of_cpus': host.cpu_configuration['nr_cpus'],
                        'xen_memory_total': int(int(host.metrics.memory_total)/(1000*1000*1000)),
                        'xen_memory_free': int(int(host.metrics.memory_free)/(1000*1000*1000)),
                        'xen_memory_used': int((int(host.metrics.memory_total)-int(host.metrics.memory_free))/(1000*1000*1000)),
                    })
                for vm_uuid in xen_vm_list:
                    vm = xen_conn.VMS.get_vm(vm_uuid)
                    if int(vm.domid) != 0:
                        xen_host_data['vms'].append({
                            'vm_domid': vm.domid,
                            'vm_name': vm.name_label,
                            'vm_power_state': vm.power_state,
                            'vm_memory_static_max': int(int(vm.memory_static_max)/(1000*1000*1000)),
                            'vm_memory_dynamic_max': int(int(vm.memory_dynamic_max)/(1000*1000*1000)),
                            'vm_vcpus': int(vm.VCPUs_max)
                        })
                return {'xenhost': xen_host_data}, 200
            else:
                return {'error': True, 'message': 'No ID Given'}, 400
        except Exception as e:
            app.logger.exception(msg="An Exception Occured")
            return {'error': True, 'message': 'An Error Occured'}, 400
