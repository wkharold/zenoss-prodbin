##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


__doc__="""BasicDataSource

Defines attributes for how a datasource will be graphed
and builds the nessesary DEF and CDEF statements for it.
"""

from Products.ZenModel import RRDDataSource
from AccessControl import ClassSecurityInfo, Permissions
from Globals import InitializeClass
from Products.ZenEvents.ZenEventClasses import Cmd_Fail
from Products.ZenUtils.Utils import executeStreamCommand
from Products.ZenWidgets import messaging
from copy import copy
import cgi, time

snmptemplate = ("snmpwalk -c%(zSnmpCommunity)s "
                "-%(zSnmpVer)s %(manageIp)s %(oid)s")

def checkOid(oid):
    import string
    for c in string.whitespace:
        oid = oid.replace(c, '')
    oid = oid.strip('.')
    numbers = oid.split('.')
    map(int, numbers)
    if len(numbers) < 3:
        raise ValueError("OID too short")
    return oid


class BasicDataSource(RRDDataSource.SimpleRRDDataSource):

    __pychecker__='no-override'

    sourcetypes = ('SNMP', 'COMMAND')

    sourcetype = 'SNMP'
    eventClass = Cmd_Fail
    oid = ''
    parser = "Auto"

    usessh = False

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id':'oid', 'type':'string', 'mode':'w'},
        {'id':'usessh', 'type':'boolean', 'mode':'w'},
        {'id':'parser', 'type':'string', 'mode':'w'},
        )

    _relations = RRDDataSource.RRDDataSource._relations + (
        )

    # Screen action bindings (and tab definitions)
    factory_type_information = (
    {
        'immediate_view' : 'editBasicDataSource',
        'actions'        :
        (
            { 'id'            : 'edit'
            , 'name'          : 'Data Source'
            , 'action'        : 'editBasicDataSource'
            , 'permissions'   : ( Permissions.view, )
            },
        )
    },
    )

    security = ClassSecurityInfo()

    def addDataPoints(self):
        """
        Overrides method defined in SimpleRRDDataSource. Only sync the
        datapoint with the datasource if the datasource type is SNMP.
        """
        if self.sourcetype == 'SNMP':
            RRDDataSource.SimpleRRDDataSource.addDataPoints(self)

    def getDescription(self):
        if self.sourcetype == "SNMP":
            return self.oid
        if self.sourcetype == "COMMAND":
            if self.usessh:
                return self.commandTemplate + " over SSH"
            else:
                return self.commandTemplate
        return RRDDataSource.RRDDataSource.getDescription(self)


    def useZenCommand(self):
        if self.sourcetype == 'COMMAND':
            return True
        return False


    def zmanage_editProperties(self, REQUEST=None):
        'add some validation'
        if REQUEST:
            oid = REQUEST.get('oid', '')
            if oid:
                try:
                    REQUEST.form['oid'] = checkOid(oid)
                except ValueError:
                    messaging.IMessageSender(self).sendToBrowser(
                        'Invalid OID',
                        "%s is an invalid OID." % oid,
                        priority=messaging.WARNING
                    )
                    return self.callZenScreen(REQUEST)

        return RRDDataSource.SimpleRRDDataSource.zmanage_editProperties(
                                                                self, REQUEST)

    def testDataSourceAgainstDevice(self, testDevice, REQUEST, write, errorLog):
        """
        Does the majority of the logic for testing a datasource against the device
        @param string testDevice The id of the device we are testing
        @param Dict REQUEST the browers request
        @param Function write The output method we are using to stream the result of the command
        @parma Function errorLog The output method we are using to report errors
        """
        out = REQUEST.RESPONSE
        # Determine which device to execute against
        device = None
        if testDevice:
            # Try to get specified device
            device = self.findDevice(testDevice)
            if not device:
                errorLog(
                    'No device found',
                    'Cannot find device matching %s.' % testDevice,
                    priority=messaging.WARNING
                )
                return self.callZenScreen(REQUEST)
        elif hasattr(self, 'device'):
            # ds defined on a device, use that device
            device = self.device()
        elif hasattr(self, 'getSubDevicesGen'):
            # ds defined on a device class, use any device from the class
            try:
                device = self.getSubDevicesGen().next()
            except StopIteration:
                # No devices in this class, bail out
                pass
        if not device:
            errorLog(
                'No Testable Device',
                'Cannot determine a device against which to test.',
                priority=messaging.WARNING
            )
            return self.callZenScreen(REQUEST)

        # Get the command to run
        command = None
        if self.sourcetype=='COMMAND':
            # to prevent command injection, get these from self rather than the browser REQUEST
            command = self.getCommand(device, self.get('commandTemplate'))           
            displayCommand = command
            if displayCommand and len(displayCommand.split()) > 1:
                displayCommand = "%s [args omitted]" % displayCommand.split()[0]
        elif self.sourcetype=='SNMP':
            snmpinfo = copy(device.getSnmpConnInfo().__dict__)
            # use the oid from the request or our existing one
            snmpinfo['oid'] = self.get('oid', self.getDescription())
            command = snmptemplate % snmpinfo
            displayCommand = command
        else:
            errorLog(
                'Test Failed',
                'Unable to test %s datasources' % self.sourcetype,
                priority=messaging.WARNING  
            )
            return self.callZenScreen(REQUEST)
        if not command:
            errorLog(
                'Test Failed',
                'Unable to create test command.',
                priority=messaging.WARNING
            )
            return self.callZenScreen(REQUEST)
        header = ''
        footer = ''
        # Render
        if REQUEST.get('renderTemplate', True):
            header, footer = self.commandTestOutput().split('OUTPUT_TOKEN')

        out.write(str(header))

        write("Executing command\n%s\n   against %s" % (displayCommand, device.id))
        write('')
        start = time.time()
        try:
            executeStreamCommand(command, write)
        except:
            import sys
            write('exception while executing command')
            write('type: %s  value: %s' % tuple(sys.exc_info()[:2]))
        write('')
        write('')
        write('DONE in %s seconds' % long(time.time() - start))
        out.write(str(footer))

    security.declareProtected('Change Device', 'manage_testDataSource')
    def manage_testDataSource(self, testDevice, REQUEST):
        ''' Test the datasource by executing the command and outputting the
        non-quiet results.
        '''
        # set up the output method for our test
        out = REQUEST.RESPONSE
        def write(lines):
            ''' Output (maybe partial) result text.
            '''
            # Looks like firefox renders progressive output more smoothly
            # if each line is stuck into a table row.
            startLine = '<tr><td class="tablevalues">'
            endLine = '</td></tr>\n'
            if out:
                if not isinstance(lines, list):
                    lines = [lines]
                for l in lines:
                    if not isinstance(l, str):
                        l = str(l)
                    l = l.strip()
                    l = cgi.escape(l)
                    l = l.replace('\n', endLine + startLine)
                    out.write(startLine + l + endLine)

        # use our input and output to call the testDataSource Method
        errorLog = messaging.IMessageSender(self).sendToBrowser
        return self.testDataSourceAgainstDevice(testDevice,
                                                REQUEST,
                                                write,
                                                errorLog)

    def parsers(self):
        from Products.DataCollector.Plugins import loadParserPlugins
        return sorted(p.modPath for p in loadParserPlugins(self.getDmd()))



InitializeClass(BasicDataSource)
