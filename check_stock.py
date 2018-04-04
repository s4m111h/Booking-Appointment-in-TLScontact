"""
A simple script to check the available stock of Louis Vitton.
Copyright (c) 2018 N00d1e5. All Rights Reserved.
"""

__author__ = "N00d1e5"

import argparse
import datetime
import logging
import requests
import signal
from sys import exit
from time import sleep

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.header import Header

GOODS_LINK = "https://fr.louisvuitton.com/fra-fr/produits/nano-speedy-monogram-010575"
NO_AVALIABLE = "INDISPONIBLE"

signal.signal(signal.SIGINT, lambda s, f: sys.exit())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# def check_stock(session, delay):  # Check if the goods always on stock
def check_stock(delay):  # Check if the goods always on stock
    logger.info("\nPress Ctrl+C to stop.\n")

    while(1):
        # r = session.get(GOODS_LINK)
        r = requests.get(GOODS_LINK, timeout=500)
        check_time = datetime.datetime.now()

        if (NO_AVALIABLE not in r.text):
            return True

        logger.info("[Checked at %s:%s]" % (str(check_time.hour).zfill(2), str(check_time.minute).zfill(2)))
        sleep(delay)


def mail_me():  # Temporary solution, maybe in spam
    user = 'n00d1e5@sina.com'  # Suggest to use mail.sina.cn
    pwd = 'MotdePasse'  # Password of sina mail
    to = ['bowenachat@gmail.com']  # Destination mail address
    msg = MIMEMultipart()
    msg['Subject'] = Header('The goods is available', 'utf-8')
    msg['From'] = Header(user)  # Header(user)

    text = "The goods is available."
    content1 = MIMEText((text + '\n' + GOODS_LINK), 'plain', 'utf-8')
    msg.attach(content1)

    s = smtplib.SMTP('smtp.sina.com')  # SMTP server of sina mail
    s.login(user, pwd)
    s.sendmail(user, to, msg.as_string())
    s.close()
    exit("Go: %s" % (GOODS_LINK))


# Action
if __name__ == '__main__':  # execute only if run as a script
    parser = argparse.ArgumentParser(description="Script to check the available stock of Louis Vitton.")
    parser.add_argument('-d', '--delay', type=int, default=300, help='delay between attempts, in seconds (default: 300)')
    args = parser.parse_args()

    # s = requests.session()
    # if (check_stock(s, args.delay)):
    if (check_stock(args.delay)):
        mail_me()
