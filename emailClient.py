#!/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import poplib
import ConfigParser
import sys
import email
import os
import re
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time


CONFIG=None
CONFIG_SECTION= os.environ.get("CONFIG_SECTION","email")

def getConfig(option, defaultValue):
    try:
        return CONFIG.get(CONFIG_SECTION,option)
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
    user = CONFIG.get(CONFIG_SECTION,"user")
    password = CONFIG.get(CONFIG_SECTION,"password")
    ssl = bool(getConfig("smtp_ssl",False))
    port = int(getConfig("smtp_port",25))
    host = getConfig("smtp_server","relay.plus.net")

    msg = MIMEMultipart()
    subject = path+" at "+time.strftime("%Y-%m-%d %H:%M:%S")
    msg['Subject'] = subject
    msg['From'] = fromAddress
    msg['To'] = toAddress

    fp = open(path, "rb")
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    text = MIMEText(subject)
    msg.attach(text)

    s = smtplib.SMTP(host,port=port)
    if ssl:
        s.starttls()

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

def isLatest(e):
    payload = e.get_payload()
    subject = e.get("Subject")

    if "latest" in subject.lower():
        return True

    if isinstance(payload,list):
        for p in payload:
            if isLatest(p):
                return True
    else:
        if "latest" in payload.lower():
            return True

    return False


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
    if isLatest(e):
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
    user = CONFIG.get(CONFIG_SECTION,"user")
    password = CONFIG.get(CONFIG_SECTION,"password")
    global ALLOWED_EMAIL
    ALLOWED_EMAIL = CONFIG.get(CONFIG_SECTION,"approvedEmail").split(",")

    ssl = bool(getConfig("pop3_ssl",False))
    port = int(getConfig("pop3_port",110))
    server = getConfig("pop3_server","mail.plus.net")

    print("user:",user)

    if ssl:
        pop = poplib.POP3_SSL(server,port)
    else:
        pop = poplib.POP3(server,port)

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
    global CONFIG_SECTION
    parser = argparse.ArgumentParser()

    parser.add_argument("-1",dest="one", help="Run only one time",
        action="store_true")
    parser.add_argument("--section", help="Config section to use",default=CONFIG_SECTION)

    args = parser.parse_args(argv[1:])

    CONFIG_SECTION=args.section
    if args.one:
        return oneCheck()
    while True:
        oneCheck()
        time.sleep(60)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
