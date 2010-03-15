###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
from Products.ZenUtils.Ext import DirectRouter
from Products.Zuul.decorators import require
from Products.ZenUtils.json import unjson
from Products import Zuul

log = logging.getLogger('zen.NetworkRouter')

class NetworkRouter(DirectRouter):
    def __init__(self, context, request):
        super(NetworkRouter, self).__init__(context, request)
        self.api = Zuul.getFacade('network')

    def getTree(self, id='/zport/dmd/Networks'):
        return self._getNetworkTree(self.context.dmd.restrictedTraverse(id))

    def _getNetworkTree(self, thisSubnet):
        net_list = []
        for network in thisSubnet.children():
            net_list.append(self._createTreeNode(network))
            net_list[-1]['children'] = self._getNetworkTree(network)
        return net_list
    
    def _createTreeNode(self, thisSubnet):
        path = thisSubnet.getDmdKey()
        if path.startswith('/') :
            path = path[1:]

        subnets = thisSubnet.children()
        leaf = (subnets == [])

        text = thisSubnet.id + '/' + str(thisSubnet.netmask)
        if not leaf:
            text = {'count': len(subnets),
                    'text': text,
                    'description': ('subnets', 'subnet')[len(subnets) == 1]}

        return {'uid': thisSubnet.getPrimaryId(),
                'children': [],
                'path': path,
                'id': thisSubnet.getPrimaryId().replace('/', '.'),
                'uiProvider': 'network',
                'leaf': leaf,
                'text': text }

    def getInfo(self, uid, keys=None):
        service = self.api.getInfo(uid)
        data = Zuul.marshal(service, keys)
        disabled = not Zuul.checkPermission('Manage DMD')
        return {'data': data, 'disabled': disabled, 'success': True}

    def setInfo(self, **data):
        if not Zuul.checkPermission('Manage DMD'):
            raise Exception('You do not have permission to save changes.')
        service = self.api.getInfo(data['uid'])
        Zuul.unmarshal(data, service)
        return {'success': True}

    def getIpAddresses(self, uid, start=0, params=None, limit=50, sort='name',
                   order='ASC'):
        if isinstance(params, basestring):
            params = unjson(params)
        instances = self.api.getIpAddresses(uid=uid, start=start, params=params,
                                          limit=limit, sort=sort, dir=order)

        keys = ['name', 'device', 'interface', 'pingstatus', 'snmpstatus', 'uid']
        data = Zuul.marshal(instances, keys)
        return {'data': data, 'success': True}