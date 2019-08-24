#!/usr/bin/env python3

import argparse
import base64
import random
import re
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.request

try:
    from colorama import Fore, Style
    from github import Github, GithubException

except ImportError as e:
    print(e)
    sys.exit()

banner = '''
  ______ _           _  _____           _       _   
 |  ____(_)         | |/ ____|         (_)     | |  
 | |__   _ _ __   __| | (___   ___ _ __ _ _ __ | |_ 
 |  __| | | '_ \ / _` |\___ \ / __| '__| | '_ \| __|
 | |    | | | | | (_| |____) | (__| |  | | |_) | |_ 
 |_|    |_|_| |_|\__,_|_____/ \___|_|  |_| .__/ \__|
                                         | |        
                                         |_| 
'''

print(Fore.YELLOW+banner+Style.RESET_ALL+"Version: 1.1\nBy 0x41CoreDump\n\n")

parser = argparse.ArgumentParser(description='Scrape Scripts From Google And Github')

parser.add_argument('-u', '--url', type=str, help='The Target Domain', required=True)
parser.add_argument('--include-unresolvable', action='store_true', help='Include Non Resolvable URLs To The List', required=False)
parser.add_argument('-e', '--extension', type=str, default='js', help='What Extension To Look For, Default: js')
parser.add_argument('-gop', '--google_pages', type=int, default=15, help='How Many Google Pages To Search, Default: 15')
parser.add_argument('-gip', '--github_pages', type=int, default=5, help='How Many Github Pages To Search, Default: 5')
parser.add_argument('-o', '--output', type=str, required=False)

args = parser.parse_args()

RE_GOOGLE_URL = r'(?<=\<div class=\"r\"\>\<a href\=\")https?://[a-zA-Z\.0-9\/\@-]*(?=\")'
RE_VALID_ARGS_URL = r'[a-z0-9\.]+\.[a-z]+'
GOOGLE_TLDS = ['de', 'com', 'dk', 'com.au', 'se', 'fr', 'es', 'pt', 'pl', 'ca', 'at']
GITHUB_TOKEN = 'YOUR_KEY_HERE'

valid_js_urls = []
google_finished = False
github_finished = False


def printWarning(text):
    print('['+Fore.YELLOW+'!'+Style.RESET_ALL+'] '+text)

def printFailure(text):
    print('['+Fore.RED+'!'+Style.RESET_ALL+'] '+text)

def printSuccess(text):
    print('['+Fore.GREEN+'+'+Style.RESET_ALL+'] '+text)

def printInfo(text):
    print('['+Fore.BLUE+'-'+Style.RESET_ALL+'] '+text)

def resolve_and_test(url_list, source):

    global valid_js_urls 

    splitted_u = args.url.split(".")

    tld = splitted_u[len(splitted_u)-1]
    splitted_u.remove(tld)
    u = ".".join(splitted_u)

    re_valid_js_url = r'[a-z\.]*{}\.{}[a-zA-Z0-9/\.\-]*\.{}'.format(u, tld, args.extension)

    for url in url_list:

        if source == 'Google':

            try:
                request_bytes = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}), timeout=4)

            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout):
                continue

            try:
                source_code = request_bytes.read().decode("utf-8")

            except (UnicodeDecodeError, socket.timeout):
                continue           

            request_bytes.close()

        else:

            try:
                source_code = str(base64.b64decode(url.content.strip()))

            except (GithubException, TypeError) as e:
                if 'NoneType' in str(e):
                    continue

                else:
                    printWarning('Mission Failed: Github Blocked Us.')
                    break

        if not re.search(re_valid_js_url, source_code):
            continue

        for valid_url in re.findall(re_valid_js_url, source_code):

            if not args.include_unresolvable:

                for proto in ['http://', 'https://']:

                    try:
                        test_request = urllib.request.urlopen(urllib.request.Request(proto+valid_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}), timeout=4)

                        if valid_url not in valid_js_urls:
                            printSuccess('Found ({}): {}'.format(source, valid_url))
                            valid_js_urls.append(valid_url)

                            if args.output:
                                open(args.output, 'a', 1).write(valid_url+'\n')

                            break

                    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout):
                        continue
            
            else:

                if valid_url not in valid_js_urls:
                    printSuccess('Found ({}): {}'.format(source, valid_url))
                    valid_js_urls.append(valid_url)

                    if args.output:
                        open(args.output, 'a', 1).write(valid_url+'\n')
        
        time.sleep(1)
        
def search_google():

    global google_finished
    
    printInfo('Searching Google...')

    googleBlocked = False

    while not googleBlocked:

        query = '"{}"+"{}"'.format(args.url, args.extension)
        found_urls = []

        for start in range(0,(args.google_pages*10)+10,10):

            google_search_url = 'https://google.{}/search?q={}&start={}'.format(random.choice(GOOGLE_TLDS), query, start) # Random TLDs To Avoid A Fast Ban

            try:
                google_search_bytes = urllib.request.urlopen(urllib.request.Request(google_search_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}), timeout=4)

            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:

                if '429' in str(e):
                    printWarning('Mission Failed: Google Blocked Us.')
                    resolve_and_test(found_urls, 'Google')
                    googleBlocked = True
                    break

                else:
                    printWarning('Unable To Connect To {}. Are You Connected To The Internet?'.format(google_search_url))

            google_search_results = google_search_bytes.read().decode('utf-8')

            google_search_bytes.close()

            if not re.search(RE_GOOGLE_URL, google_search_results):
                break
            
            for found_url in re.findall(RE_GOOGLE_URL, google_search_results):
                found_urls.append(found_url)

            time.sleep(1)

        resolve_and_test(found_urls, 'Google')

        googleBlocked = True

    printInfo('Finished Google Look-Up!')

    google_finished = True

def search_github():

    global github_finished

    printInfo('Searching Github...')

    githubBlocked = False

    g = Github(GITHUB_TOKEN)

    while not githubBlocked:

        found_urls = []

        github_search_asc = g.search_code(args.url+' '+args.extension, order='asc')

        github_search_desc = g.search_code(args.url+' '+args.extension, order='desc')

        for index in range((args.github_pages*10)+1):

            try:
                found_url = github_search_asc[index]

            except (GithubException, IndexError) as e:
                if 'index' in str(e):
                    break
                
                else:
                    printWarning('Mission Failed: Github Blocked Us.')
                    resolve_and_test(found_urls)
                    githubBlocked = True
                    break                

            if found_url not in found_urls:
                found_urls.append(found_url)
            
            try:
                found_url = github_search_desc[index]

            except (GithubException, IndexError) as e:
                if 'index' in str(e):
                    break

                else: 
                    printWarning('Mission Failed: Github Blocked Us.')
                    resolve_and_test(found_urls, 'Github')
                    githubBlocked = True
                    break

            if found_url not in found_urls:
                found_urls.append(found_url)

            time.sleep(1)

        resolve_and_test(found_urls, 'Github')

        githubBlocked = True

    printInfo('Finished Github Look-Up!')
    
    github_finished = True

def checkArgs():

    if len(args.extension.split(',')) > 1:
        printFailure('Only One Extension Allowed.')
        sys.exit()

    if not re.search(RE_VALID_ARGS_URL, args.url):
        printFailure('Invalid URL! Try Something Like: www.example.com')
        sys.exit()

    try:
        Github(GITHUB_TOKEN).get_user('0x41CoreDump')

    except GithubException:
        printFailure('Invalid Github Token!')
        sys.exit()

def main():

    global google_finished
    global github_finished

    checkArgs()

    github_thread = threading.Thread(target=search_github)
    github_thread.daemon = True
    github_thread.start()
    
    google_thread = threading.Thread(target=search_google)
    google_thread.daemon = True
    google_thread.start()

    def keyboardinterrupt(*args):
        print()
        printWarning('Quitting...')
        sys.exit()

    signal.signal(signal.SIGINT, keyboardinterrupt)

    while not google_finished or not github_finished:
        pass

    if args.output:
        printInfo('Saved The Output In: {}'.format(args.output))

    printSuccess('Finished!')

    sys.exit()

if __name__ == '__main__':
    main()


