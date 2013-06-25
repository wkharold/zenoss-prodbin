##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################

from Products.ZenTestCase.BaseTestCase import BaseTestCase

class TestPublish(BaseTestCase):

    def afterSetUp(self):
        super(TestPublish, self).afterSetUp()

        # Make a valid test device
        testdev = str(self.__class__.__name__)

        self.name = testdev

        # rpub = RedisPublisher()

    def TestPublish(self):
        """
        Sanity check to make sure that Redis stores work
        """
        # rpub = RedisPublisher()

        # Create a new file, and add a value after creation
        self.assertEquals( rpub.put("name", "42"), None )

    def testQueuedPublish(self):
        """
        Redis not up queue metrics (and send an event)
        """
        pass

    def beforeTearDown(self):
        """
        Clean up after our tests
        """
        super(TestPublish, self).beforeTearDown()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPublish))
    return suite
