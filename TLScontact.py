"""
A simple script to check the available appointment of TLScontact.
Copyright (c) 2018 N00d1e5. All Rights Reserved.
"""

#!/usr/bin/python

import argparse
import datetime
import logging
import requests
import signal
import subprocess
import sys
import time
from bs4 import BeautifulSoup

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.header import Header

__author__ = "N00d1e5"

TLS = 'https://fr.tlscontact.com/'  # Main part of url
IND = '/index.php'  # Homepage with location
CNX = '/login.php'  # Connexion page
APP = '/myapp.php'  # Application page
FORBIDDEN_WORD = 'TLScontact | Security Notice'  # Block notice
BLOCK_WORD = 'Please try connecting again later.'  # Block notice
APPOINTMENT_GOT = 'Appointment Confirmation with TLScontact'  # Appointment check
PREPERE_STUFF = 'map to access TLScontact'
LIST_CONTURY_CITY = [
    'dz', ['ALG', 'ORN', 'AAE'], 'cn', [
        'BJS', 'TNA', 'XIY', 'SHA', 'HGH', 'NKG', 'CAN', 'SZX', 'FOC', 'CNG',
        'CKG', 'KMG', 'WUH', 'CSX', 'SHE'
    ], 'eg', ['CAI', 'ALY'], 'id', ['JKT'], 'lb', ['BEY'], 'th', ['BKK'], 'gb',
    ['LON', 'EDI'], 'uz', ['TAS'], 'vn', ['HAN', 'SGN']
]  # source from https://fr.tlscontact.com/
week = [
    'Monday', 'Tuesday', 'Wednesday', 'Thurday', 'Friday', 'Saturday', 'Sunday'
]

signal.signal(signal.SIGINT, lambda s, f: sys.exit())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

s = requests.session()


def main(username, password, delay, month_want, day_want):
    logger.info("\nPress Ctrl+C to stop.\n")

    while (1):
        if (not test_connexion()):
            if reconnect(username, password):
                logger.info("Authentication status: connected.\n")
            else:
                sys.exit("Connection failed.")

        req = s.get(TLS_APP)
        (year, month, day, hh, mm) = check_appiontement(req)

        if check_satisfait(year, month, day, month_want, day_want):
            logger.info(
                "++++++++++++++++++++\n++ GO and get it! ++\n+ %s-%s-%s %s:%s "
                "+\n++++++++++++++++++++\n" % (year, month, day, hh, mm))
            # get_appointment(year, month, day, hh, mm, req)
            tmp_solution(year, month, day, hour, minute)
        else:
            (y1, i1, j1, h1, m1, y2, i2, j2, h2,
             m2) = check_more_appiontements(req)
            check_time = datetime.datetime.now()
            w0 = week[datetime.date(int(year), int(month), int(day)).weekday()]
            w1 = week[datetime.date(int(y1), int(i1), int(j1)).weekday()]
            w2 = week[datetime.date(int(y2), int(i2), int(j2)).weekday()]
            logger.info(
                "Bad luck, the first three available appointments:"
                "\n[1] %s-%s-%s %s:%s %s\n[2] %s-%s-%s %s:%s %s"
                "\n[3] %s-%s-%s %s:%s %s\nIf you want one of them, "
                "book it on the TLScontact site.\n[Checked at %s:%s]\n" %
                (year, month, day, hh, mm, w0, y1, i1, j1, h1, m1, w1, y2, i2,
                 j2, h2, m2, w2, str(check_time.hour).zfill(2),
                 str(check_time.minute).zfill(2)))

        logger.debug("Try again in %ss.", delay)
        time.sleep(delay)


# Check if logged in
def test_connexion():
    logger.debug("Testing connection")
    r = s.get(TLS_APP)
    check_forbidden(r)
    # if conntected, we could get the application page
    return (r.url != TLS_IND)


# Check if blocked
def check_forbidden(r):
    logger.debug("Testing if connexion blocked")
    if ((FORBIDDEN_WORD in r.text) or (BLOCK_WORD in r.text)):
        sys.exit("Connexion blocked, please try again later.")
    else:
        return True


# Check if blocked
def check_block(r):
    logger.debug("Testing if connexion blocked")
    return ((BLOCK_WORD not in r.text))


# Reconnect in case of disconnection
def reconnect(username, password):
    logger.debug("Reconnecting")
    sid = get_sid()
    return authenticate(username, password, sid)


# Get secret ID
def get_sid():
    logger.debug("Geting secret ID")
    req = s.get(TLS_CNX)
    return (req.text.split('var secret_id = "')[1].split('";')[0])


# Log in
def authenticate(username, password, sid):
    logger.debug("Authenticating")
    payload = {
        'process': 'login',
        '_sid': sid,
        'email': username,
        'pwd': password
    }
    s.post(TLS_CNX, data=payload)
    r = s.get(TLS_APP)
    is_pass = check_forbidden(r)
    if (r.url != TLS_IND and is_pass):
        return True
    elif (not is_pass):
        sys.exit("Connexion blocked, increse valur DELAY in the code.")
    else:
        sys.exit("Connection failed, please check your information.")


# Find the earliest appointment
def check_appiontement(req):
    logger.debug("Checking avaliable appointment")

    # Are you kidding me
    if (APPOINTMENT_GOT in req.text):
        sys.exit("You have booked an appointment, call TLScontact to cancel.")
    elif ((PREPERE_STUFF not in req.text)):
        sys.exit("You have to finish to step 1 and 2 in the application.")
    elif ('dispo' not in req.text):
        sys.exit("No avaliable appointment, end of the world.")
    else:
        soup = BeautifulSoup(req.text, "lxml")
        date = soup.find_all('a', 'dispo')[0].parent.contents[0][0:-1]
        time = soup.find_all('a', 'dispo')[0].text
        (year, month, day) = date.split('-')
        (hour, minute) = time.split(':')

    return (year, month, day, hour, minute)


# Looking for other appointment
def check_more_appiontements(req):
    logger.debug("Looking for other appointments")

    soup = BeautifulSoup(req.text, "lxml")
    d1 = soup.find_all('a', 'dispo')[1].parent.contents[0][0:-1]
    d2 = soup.find_all('a', 'dispo')[2].parent.contents[0][0:-1]
    t1 = soup.find_all('a', 'dispo')[1].text
    t2 = soup.find_all('a', 'dispo')[2].text
    (y1, i1, j1) = d1.split('-')
    (y2, i2, j2) = d2.split('-')
    (h1, m1) = t1.split(':')
    (h2, m2) = t2.split(':')

    return (y1, i1, j1, h1, m1, y2, i2, j2, h2, m2)


# Check if the earliest satisfait you
def check_satisfait(year, month, day, month_want, day_want):
    logger.debug("Checking if satisfait the deadline")
    current_year = datetime.datetime.now().year
    if (int(current_year) < int(year)):
        return ((month <= (month_want + 12)) and (int(day) <= int(day_want)))
    else:
        return ((month <= month_want) and (int(day) <= int(day_want)))


# Temporary solution, maybe in spam
def tmp_solution(year, month, day, hour, minute):
    user = 'n00d1e5@sina.cn'
    pwd = 'n00d1e5'
    to = ['n00d1e5@n00d1e5.n00d1e5']
    msg = MIMEMultipart()
    msg['Subject'] = Header('Go booking the appointment', 'utf-8')
    msg['From'] = Header(user)

    text = year + '-' + month + '-' + day + ' ' + hour + ':' + minute
    content1 = MIMEText(text, 'plain', 'utf-8')
    msg.attach(content1)

    s = smtplib.SMTP('smtp.sina.cn')
    s.login(user, pwd)
    s.sendmail(user, to, msg.as_string())
    s.close()


# If you say so, get it
def get_appointment(year, month, day, hour, minute, req):
    TLS_BOOK = TLS + args.country.lower() + '/' + args.city.upper(
    ) + '/ajax/confirm_action.php'
    TLS_CONFIRME = TLS + args.country.lower() + '/' + args.city.upper(
    ) + '/action.php'

    # Need by payload
    url = 'https%3A%2F%2Ffr.tlscontact.com%2F' + args.country.lower(
    ) + '%2F' + args.city.upper() + "%2Faction.php%3Fprocess%3Dmulticonfirm"
    fg_id = req.url.split('fg_id=')[-1]
    goal1 = year + '-' + month + '-' + day + '%2B' + hour + '%253A' + minute
    goal2 = year + '-' + month + '-' + day + '%20' + hour + '%3A' + minute
    issuer_view = args.country.lower() + args.city.upper() + "2fr"
    time_post = int(time.time() * 1000)
    sid = req.text.split('var secret_id = "')[1].split('";')[0]

    url = url + '%26what%3Dtake_appointment%26fg_id%3D' + fg_id + \
          '%26result%3D' + goal1 + '%26issuer_view%3D' + issuer_view

    payload = {
        'url': url,
        'issuer_view': '',
        'target': 'ajax_form_status',
        'time': time_post,
        '_sid': sid
    }

    s.post(TLS_BOOK, data=payload)

    time_post = int(time.time() * 1000)

    payload_bis = {
        'f_id': '',
        'fg_id': fg_id,
        'what': 'take_appointment',
        'result': goal2,
        'as_u_id': '',
        '_sid': sid,
        'process': 'multiconfirm',
        'reloader_timestamp': time_post
    }
    time.sleep(2)
    s.post(TLS_CONFIRME, data=payload_bis)

    req = s.get(TLS_APP)
    if (APPOINTMENT_GOT in req.text):
        w = week[datetime.date(int(year), int(month), int(day)).weekday()]
        sys.exit("Success, appointment on %s-%s-%s %s:%s %s" %
                 (year, month, day, hour, minute, w))
    else:
        sys.exit("Something wrong, my fault...")


# Action
if __name__ == '__main__':  # execute only if run as a script
    parser = argparse.ArgumentParser(
        description="Script to check the available appointment of TLScontact.")
    parser.add_argument('login', help='TLScontact login (e-mail address)')
    parser.add_argument('password', help='TLScontact password')
    parser.add_argument(
        'country',
        help='The country code of your application center (gb for the UK)')
    parser.add_argument(
        'city',
        help='The city code of your application center (LON for London)')
    parser.add_argument(
        'month', help='The latest acceptable month with number')
    parser.add_argument('day', help='The latest acceptable day with number')
    parser.add_argument(
        '-d',
        '--delay',
        type=int,
        default=300,
        help='delay between attempts, in seconds (default: 300)')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose mode')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if (LIST_CONTURY_CITY.count(args.country.lower()) != 1
            or LIST_CONTURY_CITY[1 + LIST_CONTURY_CITY.index(
                args.country.lower())].count(args.city.upper()) != 1):
        sys.exit(
            "Check your contry code and city code, please input valid code or contact me to update."
        )

    if (((type(args.day) == int and 0 < args.day <= 31) or
         (type(args.day) == str and 0 < len(args.day) <= 2
          and 0 < int(args.day) <= 31))
            and ((type(args.month) == int and 0 < args.month <= 12) or
                 (type(args.month) == str and 0 < len(args.month) <= 2
                  and 0 < int(args.month) <= 12))):
        TLS_IND = TLS + args.country.lower() + '/' + args.city.upper() + IND
        TLS_CNX = TLS + args.country.lower() + '/' + args.city.upper() + CNX
        TLS_APP = TLS + args.country.lower() + '/' + args.city.upper() + APP
        main(args.login, args.password, args.delay, args.month, args.day)
    else:
        sys.exit("Check your month and day, please input valid numbers.")
