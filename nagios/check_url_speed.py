#!/usr/bin/env python3

import argparse
import timeit
import re
import sys
import subprocess
import os

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


def check_site_speed(site_url, debug=False):
    new_env = dict(os.environ)  # Copy current environment
    new_env['LANG'] = 'en_US.UTF-8'
    new_env['LC_ALL'] = 'en_US.UTF-8'
    if (debug):
        print("Working with URL " + site_url)
        print("Debug options is " + str(debug))
    start_time=timeit.default_timer()  # wget = subprocess.run(["export LC_ALL=en_US.UTF-8 && timeout 120 wget -E -p -Q1000K --user-agent=Mozilla --no-cache --no-cookies --delete-after --timeout=15 --tries=2 "+site_url+" | grep Downloaded | grep '\([0-9.]\+ [KM]B/s\)'"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    args = ['wget', '-E', '-p', '-Q300K', '--user-agent=Mozilla', '--no-cache', '--no-cookies', '--delete-after',
            '--timeout=15', site_url]
    # args = ["wget -E -p -Q1000K --user-agent=Mozilla --no-cache --no-cookies --delete-after --timeout=15 --tries=2 "+site_url+""]
    wget = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env)
    if (debug):
        print(str(args))

    try:
        output, error = wget.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        wget.kill()
        output, error = wget.communicate()

    try:
        # wget put data info to stderr
        data = error
        speed_temp = re.findall(r's \((.*?)B/s', str(data))
        speed_temp_si = re.findall(r's \((.*?) [KM]B/s', str(data))

        if re.findall(r'M', str(speed_temp)) == [] and re.findall(r'K', str(speed_temp)) == []:
            speed_ = "{0:.3f}".format(float(speed_temp_si[0]) * 0.001 * 8)
        elif re.findall(r'M', str(speed_temp)) != []:
            speed_ = "{0:.3f}".format(float(speed_temp_si[0]) * 1000 * 8)
        elif re.findall(r'K', str(speed_temp)) != []:
            speed_ = "{0:.3f}".format(float(speed_temp_si[0]) * 1 * 8)

        if (debug):
            print("This is stdout: {}".format(output))
            print("This is stderr: {}".format(error))
            print("return code is " + str(wget.returncode))
            print("output code is  " + str(wget.stdout))
            print("speed_temp " + str(speed_temp))
            print("speed_temp_si " + str(speed_temp_si))

        end_time = timeit.default_timer()
    except:
        speed_ = 'no_data'
        if (debug):
            print("This is stdout: {}".format(output))
            print("This is stderr: {}".format(error))
        nagiosExit(nagios.critical, "problem with loading page " + site_url)

    # print("web_speed_test:" + speed_ + " return_code:" + str(wget.returncode) + " command_run_time:" + str(
    #         end_time - start_time))
    print("return_code = {0} web_speed_test = {1} command_run_time = {2}s |web_speed_test={1};;;0.000 command_run_time={2}s;;;0.00".format(str(wget.returncode), str(speed_), str(round((end_time - start_time), 2))))
    nagiosExit(nagios.ok)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=str("Nagios-ready python script for comparing data speed retrieved from an HTTP source.\n ./check_url_speed.py --url 'https://example.org/file' "))
    parser.add_argument('-v', '--version', action="store_true", help='Show script version and exit')
    parser.add_argument('-d', '--debug', action="store_true", help='add debug data', default=False)
    parser.add_argument('-u', '--url', help="specify a target url", type=str)

    args = parser.parse_args()

    if args.version:
        show_version()
    if args.url:
        check_site_speed(site_url=args.url, debug=args.debug)
    if not args.version or args.url:
        parser.print_help()
        sys.exit(0)
