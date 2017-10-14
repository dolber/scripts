#!/usr/bin/env python3

import argparse
import sys
import requests
import subprocess
import json
import pycurl
from urllib.parse import urlparse
from io import BytesIO
import logging
import re
import time

logger = logging.getLogger('nagios-scripts')
logger.setLevel(logging.DEBUG)

# # always write everything to the rotating log files
# if not os.path.exists('logs'): os.mkdir('logs')
# log_file_handler = logging.handlers.TimedRotatingFileHandler('logs/mtsbu.log', when='M', interval=2)
# log_file_handler.setFormatter( logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s') )
# log_file_handler.setLevel(logging.DEBUG)
# logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler() # sys.stderr
console_handler.setLevel(logging.CRITICAL) # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter( logging.Formatter('[%(asctime)s - %(levelname)s](%(name)s): %(message)s') )
logger.addHandler(console_handler)


VERSION='0.1'
def show_version(): print(VERSION)

class Nagios:
    ok          = (0, 'OK')
    warning     = (1, 'WARNING')
    critical    = (2, 'CRITICAL')
    unknown     = (3, 'UNKNOWN')

nagios = Nagios()


def nagiosExit(exit_code,msg=None):
    """Exit script with a str() message and an integer 'nagios_code', which is a sys.exit level."""
    if msg:
        print(exit_code[0],exit_code[1] + " - " + str(msg))
    sys.exit(exit_code[0])

def url_request(url, expected_response_format=None, arg0=None, arg1=None, headers_only=False, debug=False):
    try:
        if headers_only == True:
            request = requests.head(url)
            print(request.headers)
        else: request = requests.get(url)

        logger.info(str("Status code: {0} :: {1}".format(request.status_code, url)))

        if request.status_code > 200:
            nagiosExit(nagios.critical, str("Status code: {0} :: {1}".format(request.status_code, url)))
        else:
            if expected_response_format == 'JSON':
                try:
                    json_response = json.loads(request.text)
                except ValueError:
                    nagiosExit(nagios.critical, str("Could not decode valid JSON at url: {0}".format(url)))
                check_json_response(json_response, check_json_key=arg0, check_json_value=arg1)
            else:
                text_response = str(request.content) #be careful on strings that could look like other types
                check_text_response(text_response, arg0)

    except requests.ConnectionError : nagiosExit(nagios.critical,str("Error loading :: {0}".format(url)))
    except requests.Timeout : nagiosExit(nagios.critical,str("Timed out :: {0}".format(url)))
    except requests.HTTPError : nagiosExit(nagios.critical,str("Invalid HTTP response :: {0}".format(url)))
    except requests.TooManyRedirects: nagiosExit(nagios.critical,str("Too many redirects :: {0}".format(url)))

def url_request_curl(url, response_text, ip, ipv6=0):

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if ":" in domain:
        port = re.search('.*:([0-9]*)', domain).group(1)
    elif parsed_url.scheme == "http":
        port = 80
    elif parsed_url.scheme == "https":
        port = 443

    logger.debug(str("get url {} via ip {}".format(url, ip)))
    logger.debug(str("domain is {} port is {} and via scheme {}".format(domain, port, parsed_url.scheme)))
    buffer = BytesIO()
    headers = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 5)
    curl.setopt(pycurl.CONNECTTIMEOUT, 30)
    curl.setopt(pycurl.TIMEOUT, 300)
    curl.setopt(pycurl.NOSIGNAL, 1)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.HEADERFUNCTION, headers.write)
    if ipv6 == 1:
        curl.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V6)
    else:
        curl.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
    if console_handler.level == 10:
        curl.setopt(pycurl.VERBOSE, 1)
    if domain and port and ip and ip != "undef":
        names = [
            "{0}:{1}:{2}".format(domain, port, ip),
            "{0}:{1}:{2}".format(domain, 443, ip),
            "{0}:{1}:{2}".format(domain, 80, ip),
            ]
        curl.setopt(pycurl.RESOLVE, names)
    try:
        curl.perform()

        body = buffer.getvalue().decode('iso-8859-1')
        headers = headers.getvalue().decode('iso-8859-1')

        logger.info("Status code: {} for url {} via ip {} and ipv6 {}".format(curl.getinfo(curl.RESPONSE_CODE), url, ip, ipv6))
        now = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
        print("Status code: {0} for url {1} via ip {2} and ipv6 {3} [{4}] |status_code={0};;;0".format(curl.getinfo(curl.RESPONSE_CODE), url, ip, ipv6, now))
        logger.debug(body)
        logger.debug(headers)

        if curl.getinfo(curl.RESPONSE_CODE) > 200:
            nagiosExit(nagios.critical, str("Status code: {0} :: {1}".format(curl.getinfo(curl.RESPONSE_CODE), url)))
        else:
            check_text_response_list(str(body), response_text)

    except pycurl.error as err:
        logger.info("Error loading :: {0} {1}".format(url, str(err)))
        nagiosExit(nagios.critical,str("Error loading :: {0} {1}".format(url, str(err))))
    finally:
        curl.close()


def check_json_response(json_response,check_json_key,check_json_value):
    """ check a json key/value pair against a HTTP response.
    match returns nagiosExit(0), otherwise nagiosExit(1) is returned.
    """
    try:
        if json_response[check_json_key] != check_json_value:
            returnValue = "Expected '{0}:{1}' ; Received '{2}'".format(check_json_key, check_json_value, json_response[check_json_key])
            nagiosExit(nagios.critical, str(returnValue))
        else:
            nagiosExit(nagios.ok)
    except KeyError:
        ''' key could not be looked up in the response data from the url '''
        nagiosExit(nagios.critical, str("KeyError :: Failed to find JSON key: {0}").format(check_json_value))


def check_text_response(text_response,expected_response_text):
    """ Simply do an equality comparison between two objects.  Caution, may do 'hilarious' things on binary data. """
    if str(expected_response_text) not in str(text_response):
        returnValue = "Expected {0} ; Received: {1}".format(expected_response_text, text_response)
        nagiosExit(nagios.critical,str(returnValue))
    else:
        nagiosExit(nagios.ok)

def check_text_response_list(text_response, expected_response_list):
    """ Simply do an equality comparison between two objects.  Caution, may do 'hilarious' things on binary data. """
    if expected_response_list:
        logger.debug("expected_response_list = {0}".format(str(expected_response_list)))
        for expected_response_text in expected_response_list:
            if str(expected_response_text) not in str(text_response):
                returnValue = "Expected {0} ; Received: {1}".format(expected_response_text, text_response)
                nagiosExit(nagios.critical,str(returnValue))

    logger.debug("nagios ok")
    nagiosExit(nagios.ok)


if __name__ == "__main__":

    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description=str("Nagios-ready python script for comparing data retrieved from an HTTP/HTTPS source.\n ./check_url.py --host 'https://example.org/file' --text 'text' "))
    parser.add_argument('-V', '--version', action="store_true", help='Show script version and exit')
    parser.add_argument('--host', '-u', help="specify a target url", type=str)
    parser.add_argument('--ip', '-I', help="specify a target ip or set undef", type=str)
    parser.add_argument('--ipv6', '-6', help="force use ipv6", type=str2bool, nargs='?', const=True, default="False" )
    parser.add_argument('--text', '-t', action="append", help="plain text to search in url (multiple options allowed)")
    parser.add_argument('-v', '--verbose', action="count", help="verbose level... repeat up to three times.")
    args = parser.parse_args()

    def set_log_level_from_verbose(args):
        if not args.verbose:
            console_handler.setLevel('ERROR')
        elif args.verbose == 1:
            console_handler.setLevel('WARNING')
        elif args.verbose == 2:
            console_handler.setLevel('INFO')
        elif args.verbose >= 3:
            console_handler.setLevel('DEBUG')
        else:
            logger.critical("UNEXPLAINED NEGATIVE COUNT!")


    set_log_level_from_verbose(args)
    if args.version:
        show_version()
    if args.text:
        logger.debug("ipv6 options is set to {}".format(args.ipv6))
        logger.debug("ip option is set to {} and type {}".format(str(args.ip), type(args.ip)))
        url_request_curl(url=args.host, response_text=args.text, ip=args.ip, ipv6=args.ipv6)
    if not args.version and not args.host:
        parser.print_help()
        sys.exit(0)
