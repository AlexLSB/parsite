# coding: utf-8


from __future__ import print_function
from time import sleep
import urllib2
import cookielib
from random import choice
from subprocess import call
from threading import Timer, Event, Thread
from urlparse import urlparse
import time
import urllib
import json

import lxml.html

#from _string_methods import get_unicode_string
def get_unicode_string(s):
    try:
        ss = s.decode('utf-8')
    except:
        ss = s
    return ss


def reconnect_modem():
    call(['data\\yandex\\reconnect.bat'])
    time.sleep(30)


if 'user01' in __file__:
    USE_PROXY = False
else:
    USE_PROXY = True

cookieJar = cookielib.CookieJar()
opener = None
user_agents = [
    # 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (Windows; I; Windows NT 5.1; ru; rv:1.9.2.13) Gecko/20100101 Firefox/4.0',
    'Opera/9.80 (Windows NT 6.1; U; ru) Presto/2.8.131 Version/11.10',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
    # 'Lynx/2.8.6rel.4 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.8g',
]


def build_opener(use_proxy=USE_PROXY):
    global opener
    if opener:
        return opener

    global cookieJar

    http_proxy_server = "proxy.ab.ru"
    http_proxy_port = "3128"
    http_proxy_realm = http_proxy_server # Worked in my (limited) testing environment.
    http_proxy_user = "APRESS+polyudov"
    http_proxy_passwd = "olega37"

    http_proxy_full_auth_string = "http://%s:%s@%s:%s" % (http_proxy_user,
                                                          http_proxy_passwd,
                                                          http_proxy_server,
                                                          http_proxy_port)\

    proxy_handler = urllib2.ProxyHandler({"http": http_proxy_full_auth_string, "https": http_proxy_full_auth_string})

    if use_proxy:
        opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cookieJar))
    else:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

    return opener


def get_string_from_url(url, use_proxy=USE_PROXY, data=None, headers=None):
    if url.split('.')[-1] in ['exe', 'pdf', 'iso', 'msi']:  # если ссылка на скачивание то пропускаем
        return ''
    url_parsed = urlparse(url)

    domain = get_unicode_string(url_parsed.hostname).encode('idna')
    path = urllib2.quote(get_unicode_string(url_parsed.path).encode('utf-8'))
    query = urllib2.quote(get_unicode_string(url_parsed.query).encode('utf-8'), safe="=|/|&|:|?%l%/:=&?~#+!$,;@()*[]<>'")
    url_new = url_parsed.scheme + '://' + domain + path + '?' + query

    opener = build_opener(use_proxy)

    full_headers = [('User-agent', choice(user_agents))]
    if headers:
        full_headers.extend(headers)
    opener.addheaders = full_headers

    done_event = Event()
    shared_with_threads = []

    def too_big(shared_with_threads):
        shared_with_threads.append('')
        try:
            download_thread._Thread__stop()
        except:
            print('error')
        done_event.set()

    def get_text(url, page):
        try:
            shared_with_threads.append(opener.open(url).read())
        except:
            shared_with_threads.append('')
        done_event.set()
        timer._Thread__stop()
    if not data:
        timer = Timer(10.0, too_big, (shared_with_threads,))
        timer.start()

        download_thread = Thread(target=get_text, args=(url_new, shared_with_threads))
        download_thread.start()

        done_event.wait()

        page = shared_with_threads[0]
        if not page:
            raise Error404('Did not load page ' + url_new)

    else:
        response = opener.open(url_new, urllib.urlencode(data))
        page = response.read()

    page = get_unicode_string(page)

    return page


def get_lxml_document_from_str(page_str):
    if not page_str:
        raise Error404(u'')
    return lxml.html.document_fromstring(page_str.replace('encoding="windows-1251"', '').replace('encoding="iso-8859-1"', '').replace('encoding="UTF-8"', '').replace('encoding="utf-8"', ''))


class Error404(Exception):
    pass


def get_lxml_document_from_url(url, use_proxy=USE_PROXY, data=None, headers=None):
    document = get_lxml_document_from_str(get_string_from_url(url, use_proxy=use_proxy, data=data, headers=headers))
    domain = get_unicode_string(urlparse(url).hostname).encode('idna')
    document.make_links_absolute('http://' + domain)
    return document


def get_json_from_url(url, use_proxy=USE_PROXY, data=None, headers=None):
    json_str = get_string_from_url(url, use_proxy=use_proxy, data=data, headers=headers)
    return get_json_from_str(json_str)


def get_json_from_str(json_str):
    return json.loads(json_str)


def internet_errors_handler(func):
    def wrapper(*args, **kwargs):
        i = 0
        while True:
            try:
                result = func(*args, **kwargs)
                break
            except Error404:
                if i > 5:
                    raise Error404('didnt load url ' + args[0])
                sleep(60 * 1)
                i += 1
        return result
    return wrapper


def internet_errors_handler_wait(func):
    def wrapper(*args, **kwargs):
        i = 0
        while True:
            try:
                result = func(*args, **kwargs)
                break
            except Error404:
                if i > 5:
                    raise Error404('didnt load url ' + args[0])
                sleep(60 * 1)
                i += 1
        sleep(3)
        return result
    return wrapper