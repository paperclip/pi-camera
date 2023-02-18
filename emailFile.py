#!/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import ConfigParser
import os
import smtplib
import sys
import time
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIG=None
CONFIG_SECTION= os.environ.get("CONFIG_SECTION","google")

def getConfig(option, defaultValue):
    try:
        return CONFIG.get(CONFIG_SECTION,option)
    except ConfigParser.NoOptionError:
        return defaultValue


def send_file(toAddress, path):
    fromAddress = "camera@leeder.plus.com"
    user = CONFIG.get(CONFIG_SECTION, "user")
    password = CONFIG.get(CONFIG_SECTION, "password")
    ssl = bool(getConfig("smtp_ssl", False))
    port = int(getConfig("smtp_port", 25))
    host = getConfig("smtp_server", "relay.plus.net")

    msg = MIMEMultipart()
    subject = path+" at "+time.strftime("%Y-%m-%d %H:%M:%S")
    msg['Subject'] = subject
    msg['From'] = fromAddress
    msg['To'] = toAddress

    fp = open(path, "rb")
    img = MIMEText(fp.read())
    fp.close()
    msg.attach(img)

    text = MIMEText(subject)
    msg.attach(text)

    s = smtplib.SMTP(host, port=port)
    if ssl:
        s.starttls()

    s.login(user, password)
    ret = s.sendmail(fromAddress, [toAddress], msg.as_string())
    s.quit()
    return ret

def setup():
    global CONFIG
    CONFIG = ConfigParser.SafeConfigParser()
    CONFIG.read("emailClient.config")

    
def main(argv):
    global CONFIG_SECTION
    parser = argparse.ArgumentParser()

    parser.add_argument("--section", help="Config section to use",default=CONFIG_SECTION)
    parser.add_argument("email")
    parser.add_argument("filename")

    args = parser.parse_args(argv[1:])

    CONFIG_SECTION=args.section
    setup()
    send_file(args.email, args.filename)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
