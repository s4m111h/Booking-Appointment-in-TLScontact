"""
A simple script to check the available appointment of TLScontact.
Copyright (c) 2014 N00d1e5. All Rights Reserved.
"""

#!/usr/bin/python
import argparse
import datetime
import logging
import requests
import signal
import sys
import time

__author__ = "N00d1e5"

# Values to change
TLS_EDI = 'https://fr.tlscontact.com/gb/EDI/index.php'  # Homepage with location
TLS_CNX = 'https://fr.tlscontact.com/gb/EDI/login.php'  # Connexion page
TLS_APP = 'https://fr.tlscontact.com/gb/EDI/myapp.php'  # Application page

FORBIDDEN_WORD = 'TLScontact | Security Notice'  # Block notice
APPOINTMENT_GOT = 'Appointment Confirmation with TLScontact'  # Appointment check

signal.signal(signal.SIGINT, lambda s, f: sys.exit())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

s = requests.session()


def main(username, password, delay, month_want, day_want):
    logger.info("Press Ctrl+C to stop")

    while (1):
        if (not test_connexion()):
            if reconnect(username, password):
                logger.info("Status: Now connected.")
            else:
                sys.exit("Connection failed.")

        (year, month, day, hour, minute) = check_appiontement()

        if check_satisfait(month, day, month_want, day_want):
            logger.info(
                "++++++++++++++++++++\n++ GO and get it! ++\n+ %s-%s-%s %s:%s "
                "+\n++++++++++++++++++++" % (month, day, hour, minute))
        else:
            logger.info("Nothing with %s-%s %s:%s" %
                        (month, day, hour, minute))

        logger.debug("Try again in %ss.", delay)
        time.sleep(delay)


# Check if logged in
def test_connexion():
    logger.debug("Testing connection")
    r = s.get(TLS_APP)
    # if conntected, we could get the application page
    return (r.url != TLS_EDI and check_forbidden(r))


# Check if blocked
def check_forbidden(r):
    logger.debug("Testing if connexion blocked")
    return (FORBIDDEN_WORD not in r.text)


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
    payload = {'process': 'login', '_sid': sid,
               'email': username, 'pwd': password}
    s.post(TLS_CNX, data=payload)
    r = s.get(TLS_APP)
    is_pass = check_forbidden(r)
    if (r.url != TLS_EDI and is_pass):
        return True
    elif (not is_pass):
        sys.exit("Connexion blocked, increse valur DELAY in the code.")
    else:
        sys.exit("Connection failed, please check your information.")


# Find the earliest appointment
def check_appiontement():
    logger.debug("Checking avaliable appointment")
    req = s.get(TLS_APP)

    # Are you kidding me
    if (APPOINTMENT_GOT in req.text):
        sys.exit("You have booked an appointment, call TLScontact to cancel.")
    elif ('dispo' not in req.text):
        sys.exit("No avaliable appointment, end of the world.")
    else:
        (date, time) = req.text.split("<a class='dispo")[0:2]
        date = date.split("overable'>")[-1].split(" <a class=")[0]
        time = time.split('</i></a>')[0][-8:]
        (year, month, day) = date.split('-')
        (hour, minute) = time.split('<i>:')[0:2]

    return (year, month, day, hour, minute)


# Check if the earliest satisfait you
def check_satisfait(year, month, day, month_want, day_want):
    logger.debug("Checking if satisfait the deadline")
    current_year = datetime.datetime.now().year
    if (int(current_year) < int(year)):
        return ((month <= (month_want + 12)) and (int(day) <= int(day_want)))
    else:
        return ((month <= month_want) and (int(day) <= int(day_want)))


# If you say so, get it
def get_appointment():
    # The appointment can't be canceled by ourselves, averse to test.
    return 0


# Action
if __name__ == '__main__':  # execute only if run as a script
    parser = argparse.ArgumentParser(
        description="Script to check the available appointment of TLScontact.")
    parser.add_argument('login', help='TLScontact login (e-mail address)')
    parser.add_argument('password', help='TLScontact password')
    parser.add_argument(
        'month', help='The latest acceptable month with number')
    parser.add_argument('day', help='The latest acceptable day with number')
    parser.add_argument('-d', '--delay', type=int, default=300,
                        help='delay between attempts, in seconds(default: 300)')
    parser.add_argument('-v', '--verbose',
                        action='store_true', help='verbose mode')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if (((type(args.day) == int and 0 < args.day <= 31) or
         (type(args.day) == str and 0 < len(args.day) <= 2 and
          0 < int(args.day) <= 31)) and
        ((type(args.month) == int and 0 < args.month <= 12) or
         (type(args.month) == str and 0 < len(args.month) <= 2 and
          0 < int(args.month) <= 12))):
        main(args.login, args.password, args.delay, args.month, args.day)
    else:
        sys.exit("Check your month and day, please input valid numbers.")
