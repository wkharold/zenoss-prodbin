###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
from zope.interface import implements
from Products.ZenModel.ChangeEvents.interfaces import IObjectModifiedEvent, \
    IObjectAddedToOrganizerEvent, IObjectRemovedFromOrganizerEvent, IDeviceClassMoveEvent
from Products.ZenModel.DeviceOrganizer import DeviceOrganizer

import logging
log = logging.getLogger('zen.modelchanges')


class ObjectModifiedEvent(object):
    """
    Fired when an object is modified.
    """
    implements(IObjectModifiedEvent)

    def __init__(self, object):
        self.object = object


class ObjectAddedToOrganizerEvent(object):
    """
    When an object is added to a new organizer
    """
    implements(IObjectAddedToOrganizerEvent)
    def __init__(self, object, organizer):
        self.object = object
        if not isinstance(organizer, DeviceOrganizer):
            raise TypeError(" %s is not an instance of Device Organizer" % organizer)
        self.organizer = organizer


class ObjectRemovedFromOrganizerEvent(object):
    """
    When an object is removed from an organizer
    """
    implements(IObjectRemovedFromOrganizerEvent)
    def __init__(self, object, organizer):
        self.object = object
        if not isinstance(organizer, DeviceOrganizer):
            raise TypeError(" %s is not an instance of Device Organizer" % organizer)
        self.organizer = organizer


class DeviceClassMovedEvent(object):
    """
    Fired when a device moves from a class to another
    """
    implements(IDeviceClassMoveEvent)

    def __init__(self, object, fromOrganizer, toOrganizer):
        self.object = object
        self.fromOrganizer = fromOrganizer
        self.toOrganizer = toOrganizer
