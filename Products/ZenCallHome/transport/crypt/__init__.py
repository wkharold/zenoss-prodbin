###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
import os
import subprocess

from Products.ZenUtils.Utils import zenPath

logger = logging.getLogger('zen.callhome')

CRYPTPATH = zenPath('Products','ZenCallHome','transport','crypt')
GPGCMD = 'gpg --batch --no-tty --quiet '

def encrypt(stringToEncrypt, publicKey):
    cmd = GPGCMD + '--keyring %s --trustdb-name %s -e -r %s' % \
          (CRYPTPATH + '/pubring.gpg', CRYPTPATH + '/trustdb.gpg', publicKey)
    
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=open(os.devnull))
    out = p.communicate(input=stringToEncrypt)[0]
    
    if p.returncode != 0:
        logger.warn('Unable to encrypt payload -- is GPG installed?')
        return None
    return out

def decrypt(stringToDecrypt, symKey):
    cmd = GPGCMD + '--passphrase %s -d' % symKey
    
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=open(os.devnull))
    out = p.communicate(input=stringToDecrypt)[0]
    
    if p.returncode != 0:
        logger.warn('Unable to decrypt payload -- is GPG installed?')
        return None
    return out
