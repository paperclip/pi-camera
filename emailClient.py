#!/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import poplib
import ConfigParser
import sys
import email
import os
import re
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


CONFIG=None

def getConfig(option, defaultValue):
    try:
        return CONFIG.get("email",option)
    except ConfigParser.NoOptionError:
        return defaultValue


def getPhotoDirConfig():
    return getConfig("image_dir","~/webdata/camera")

def getPhotoDir():
    c = getPhotoDirConfig()
    return os.path.expanduser(c) or c

def getLatestImagePath():
    photoDir = getPhotoDir()
    contents = os.listdir(photoDir)
    contents.sort()
    return os.path.join(photoDir,contents[-1])

def sendLatestImage(toAddress):
    path = getLatestImagePath()
    fromAddress = getConfig("email","camera@leeder.plus.com")
    user = CONFIG.get("email","user")
    password = CONFIG.get("email","password")

    msg = MIMEMultipart()
    msg['Subject'] = path
    msg['From'] = fromAddress
    msg['To'] = toAddress

    fp = open(path, "rb")
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    s = smtplib.SMTP(getConfig("smtp_server","relay.plus.net"))
    # s.starttls()
    s.login(user, password)
    ret = s.sendmail(fromAddress, [toAddress], msg.as_string())
    s.quit()

    print("SEND LATEST IMAGE",path,"to",toAddress,"from",fromAddress,str(ret))
    return True

ALLOWED_EMAIL = None

def whitelistAddress(addr):
    if addr in ALLOWED_EMAIL:
        return True
    return False

def extractEmail(addr):
    RE = re.compile(r"^[^<]* <([^>]+)>$")
    mo = RE.match(addr)
    if not mo:
        return addr
    return mo.group(1)

def handleEmail(text):
    text = "\n".join(text)
    e = email.message_from_string(text)
    fromAddress = e.get("From")
    fromAddress = extractEmail(fromAddress)
    if fromAddress is None:
        return
    if not whitelistAddress(fromAddress):
        return True

    payload = e.get_payload()
    if "latest" in payload:
        return sendLatestImage(fromAddress)
    else:
        print("Failed to understand command:",repr(payload))
        for part in e.walk():
            print(part.get_content_type())
            print(text)

    return False

def oneCheck():
    global CONFIG
    CONFIG = ConfigParser.SafeConfigParser()
    CONFIG.read("emailClient.config")
    user = CONFIG.get("email","user")
    password = CONFIG.get("email","password")
    global ALLOWED_EMAIL
    ALLOWED_EMAIL = CONFIG.get("email","approvedEmail").split(",")
    print("user:",user)
    pop = poplib.POP3(CONFIG.get("email","pop3_server"))
    pop.set_debuglevel(1)
    print(pop.getwelcome())
    pop.user(user)
    pop.pass_(password)

    numMessages = len(pop.list()[1])
    for i in range(numMessages):
        lines = pop.retr(i+1)[1]
        delete = handleEmail(lines)
        if delete:
            print("DELETE",i+1)
            pop.dele(i+1)

    pop.quit()
    return 0

def main(argv):
    return oneCheck()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
