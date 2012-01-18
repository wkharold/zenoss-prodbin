###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
__doc__ = """
Adds the ifOperStatus datasource and datapoint to the ethernetCsmacd_64 template at
the device level. This is so the Operational status column on the component interface panel
shows the correct value.
"""

import Migrate
import logging
from Products.ZenModel.BasicDataSource import BasicDataSource
log = logging.getLogger('zen.migrate')


class ifOperStatusEthernetCsmacd64(Migrate.Step):
    version = Migrate.Version(4, 2, 0)

    def cutover(self, dmd):
        if hasattr(dmd.Devices.rrdTemplates, 'ethernetCsmacd_64'):
            template = dmd.Devices.rrdTemplates._getOb('ethernetCsmacd_64')

            if not hasattr(template.datasources, "ifOperStatus"):
                bds = BasicDataSource('ifOperStatus')
                bds.oid = ".1.3.6.1.2.1.2.2.1.8"
                bds.sourcetype = "SNMP"
                template.datasources._setObject('ifOperStatus', bds)
                bds = template.datasources.ifOperStatus
                bds.addDataPoints()
                datapoint = template.datasources.ifOperStatus.datapoints.ifOperStatus
                datapoint.createCmd = "\n".join((
                'RRA:LAST:0.5:1:600',
                    'RRA:AVERAGE:0.5:1:600',   # every 5 mins for 2 days
                    'RRA:AVERAGE:0.5:6:600',   # every 30 mins for 12 days
                    'RRA:AVERAGE:0.5:24:600',  # every 2 hours for 50 days
                    'RRA:AVERAGE:0.5:288:600',  # every day for 600 days
                    'RRA:MAX:0.5:6:600',
                    'RRA:MAX:0.5:24:600',
                    'RRA:MAX:0.5:288:600',
                    ))


ifOperStatusEthernetCsmacd64 = ifOperStatusEthernetCsmacd64()
