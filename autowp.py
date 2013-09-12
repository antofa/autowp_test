# coding: utf-8
import httplib
import os,cookielib,urllib2
import re, csv, sqlite3
from time import sleep
from TorCtl import TorCtl
import ConfigParser
import socket


def yoip():
    global opener
    try: 
        ip = re.search("<span class='ip'>([^<]+)</span>", opener.open('http://yoip.ru').read()).group(1)
    except:
        ip = 'Unknown'
    return ip
    

def open_url(url):
    global opener
    f = False
    page = ''

    c = 0
    while not(f):
        try:
            page = opener.open(url).read()
            sleep(request_timeout)
            f = True
        except Exception, e:
            print str(e)
            if use_tor and str(e) == 'HTTP Error 509: Bandwidth Limit Exceeded':
                opener = urllib2.build_opener(proxy_support)
                # Change IP in Tor
                print "Renewing tor route wait a bit for 5 seconds"
                conn = TorCtl.connect(passphrase="1234qwer")
                conn.sendAndRecv('signal newnym\r\n')
                conn.close()
                sleep(5)
                ip = yoip()
                print "IP changed to", ip
                c = 0
            c += 1
            if c > 5:
                f = True
                page = 'error'
                print 'error'
            sleep(repeat_timeout)

    return page

conn = sqlite3.connect('autowp.db', timeout=300)
conn.text_factory = str
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS [generation] (
  [id] INTEGER PRIMARY KEY,
  [mark] CHAR,
  [model] CHAR,
  [generation] CHAR,
  [path] CHAR);''')
conn.commit()
cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS [id] ON [generation] ([id]);')
conn.commit()
cur.execute('''
CREATE TABLE IF NOT EXISTS [picture] (
  [id] CHAR,
  [generation_id] INTEGER,
  [url] CHAR,
  [is_saved] BOOLEAN);''')
conn.commit()
cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS [id] ON [picture] ([id]);')
conn.commit()

SiteUrl='http://www.autowp.ru'

socket.setdefaulttimeout(300)
proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"} )

cj = cookielib.CookieJar()
opener = urllib2.build_opener()
urllib2.install_opener(opener)

section = 'autowp'
config = ConfigParser.RawConfigParser()
config.readfp(open('settings.ini'))

request_timeout = config.getint(section, 'request_timeout')
repeat_timeout = config.getint(section, 'repeat_timeout')
start_mark = config.get(section, 'start_mark')
use_tor = config.getboolean(section, 'use_tor')

page = open_url(SiteUrl + '/brands/manufacturer')

re1 = '<h4>[^<]+<a href="/([^"]+)/"'
re2 = '<ul class="nav nav-list">(.*?)</ul>'
re4 = '<div class="thumbnail">[^<]*<a href="/picture/([^"]+)">[^<]*<img[^>]*?title="([^"]+)"'
re5 = "'(\d{4}.*)"
re6 = '<a class="thumbnail" href="([^"]+)"'

marks = re.findall(re1, page)
num_marks = len(marks)
num_mark = 0
f = 0 

for mark in marks:
    num_mark += 1
    if mark == start_mark :
        f = 1
    if mark == 'pacific':
        f = 0
    if not(f):
        continue
        
    print '\nMark: %s [%s/%s]' % (mark, num_mark, num_marks)
    re3 = '<a href="/%s/([^/]+)/">[^<]+</a>' % mark
    page = open_url('%s/%s/' % (SiteUrl, mark))
    models_block = re.search(re2, page, re.DOTALL).group(1)

    models = re.findall(re3, models_block)
    num_models = len(models)
    num_model = 0

    for model in models:
        num_model += 1
        print '\nModel: %s [%s/%s]' % (model, num_model, num_models)
        print '%s/%s/%s/pictures' % (SiteUrl, mark, model)
        
        try:
            page = open_url('%s/%s/%s/pictures' % (SiteUrl, mark, model))
        except Exception as e:
            print e

        pictures = re.findall(re4, page)
        num_pictures = len(pictures)
        num_picture = 0
        for picture in pictures:
            num_picture += 1
            try:
                generation = re.search(re5, picture[1]).group(1)
                print '%s [%s/%s]' % (picture[0], num_picture, num_pictures)
                if cur.execute("SELECT id FROM picture WHERE id = '%s'" % picture[0]).fetchone() != None:
                    continue

                # check here if pucture's id already exists
                if cur.execute("SELECT id FROM generation WHERE mark = '%s' AND model = '%s' AND generation = '%s'" % (mark, model, generation)).fetchone() == None:
                    cur.execute("INSERT INTO GENERATION (mark, model, generation) VALUES ('%s', '%s', '%s')" % (mark, model, generation)).fetchone()

                generation_id = cur.execute("SELECT id FROM generation WHERE mark = '%s' AND model = '%s' AND generation = '%s'" % (mark, model, generation)).fetchone()[0]

                page = open_url('%s/picture/%s' % (SiteUrl, picture[0]))
                img_url = re.search(re6, page).group(1)

                info = [picture[0], generation_id, SiteUrl + img_url, '0']
                cur.execute('INSERT INTO picture values (?'+',?'*3+')',[i for i in info])
                conn.commit()
            except Exception as e:
                print e