######################################################################
#
# Copyright 2010 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
import transaction
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from zope.interface import implements
from Products.ZenMessaging.queuemessaging.interfaces import IQueuePublisher
from Products.ZenMessaging.queuemessaging.adapters import EventProtobuf as Serializer
from Products.ZenMessaging.queuemessaging.publisher import EventPublisher, getModelChangePublisher
from zenoss.protocols.protobufs.zep_pb2 import RawEvent
from Products.ZenEvents.Event import buildEventFromDict


log = logging.getLogger("zen.dynamicservices")


class MockQueuePublisher(object):
    """
    This is the fake queue we are putting in place for the unit tests to test
    transactions.
    """
    implements(IQueuePublisher)

    def __init__(self):
        self.msgs = []

    def publish(self, *args, **kwargs):
        self.msgs.append( (args, kwargs))


class TestPublishEvents(BaseTestCase):

    def setUp(self):
        super(TestPublishEvents, self).setUp()
        self.publisher = getModelChangePublisher()
        from zope.component import getGlobalSiteManager
        # register the component
        gsm = getGlobalSiteManager()
        queue = MockQueuePublisher()
        gsm.registerUtility(queue, IQueuePublisher)
        self.queue = queue
        # create a dummy device
        self.device = self.dmd.Devices.createInstance('testDevice')
        self.publisher.publishAdd(self.device)


    def tearDown(self):
        super(TestPublishEvents, self).tearDown()
        self.publisher = None
        self.device = None
        self.queue = None

    def _createDummyEvent(self):
        """
        creates a dummy event
        """
        device = self.device
        eventData = dict(
            device= device.id,
            component= "",
            eventClass= "/Status/Snmp",
            eventKey="pepe1",
            summary= "2.5 second timeout connecting to device 10.87.209.147",
            message= "2.5 second timeout connecting to device 10.87.209.147",
            severity= 4,
            eventState= 0,
            eventClassKey= "testEventClassKey",
            eventGroup= "SnmpTest",
            stateChange= "2010-09-24 07:12:19",
            count= 1,
            prodState= 1000,
            suppid= "",
            manager= "localhost",
            agent= "zenperfsnmp",
            DeviceClass= "/Server/Darwin",
            Location= "testLocation",
            Systems= "System1|System2",
            DeviceGroups= "Group1|Group2",
            ipAddress= "10.87.209.147",
            facility= "unknown",
            priority= 1,
            ownerid = "admin",
            ntevid= 0,
            evid="123456789",
            DevicePriority= 3,
            monitor= "localhost")
        return buildEventFromDict(eventData)

    def testAdaptingEventtoProtobuf(self):
        # setup event and device
        device = self.device
        event = self._createDummyEvent()
        event.detaildata = dict(foo="bar")
        proto = RawEvent()
        serializer = Serializer(event)
        
        # fill the protobuf
        proto = serializer.fill(proto)

        # check the results
        self.assertEqual(proto.agent, event.agent)
        self.assertEqual(proto.event_key, event.eventKey)
        
        # make sure the actor was set
        self.assertEqual(proto.actor.element_identifier, device.id)
        # make sure we have at least one detail
        self.assertTrue(len(proto.details) >= 1)
        # the new severity value
        self.assertEqual(proto.severity, 5)

    def testFacilityConversion(self):        
        event = self._createDummyEvent()
        proto = RawEvent()
        serializer = Serializer(event)
        event.facility = "1"
        # fill the protobuf
        proto = serializer.fill(proto)
        # should have converted to an int
        self.assertEqual(proto.syslog_facility, 1)
        self.assertEqual(proto.event_class_key, event.eventClassKey)
        
    def testUsingPublisher(self):        
        event = self._createDummyEvent()
        publisher = EventPublisher()        
        publisher.publish(event)        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    #suite.addTest(makeSuite(TestPublishEvents))
    suite.addTest(makeSuite(BaseTestCase))
    return suite