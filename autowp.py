# coding: utf-8
import httplib
import os,cookielib,urllib2
import re, csv, sqlite3
from time import sleep
from TorCtl import TorCtl

request_timeout = 3
repeat_timeout = 3
use_tor = True

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
                import time
                time.sleep(5)
                print "IP changed"
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

proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"} )

cj = cookielib.CookieJar()
opener = urllib2.build_opener()
urllib2.install_opener(opener)

page = open_url(SiteUrl + '/brands/manufacturer')

re1 = '<h4>[^<]+<a href="/([^"]+)/"'
re2 = '<ul class="nav nav-list">(.*?)</ul>'
re4 = '<div class="thumbnail">[^<]*<a href="/picture/([^"]+)">[^<]*<img[^>]*?title="([^"]+)"'
re5 = "'(\d{4}.*)"
re6 = '<a class="thumbnail" href="([^"]+)"'

marks = re.findall(re1, page)

for mark in marks:
    print '\nMark:', mark
    re3 = '<a href="/%s/([^/]+)/">[^<]+</a>' % mark
    page = open_url('%s/%s/' % (SiteUrl, mark))
    models_block = re.search(re2, page, re.DOTALL).group(1)

    models = re.findall(re3, models_block)

    for model in models:
        print '\nModel', model
        print '%s/%s/%s/pictures' % (SiteUrl, mark, model)
        
        try:
            page = open_url('%s/%s/%s/pictures' % (SiteUrl, mark, model))
        except Exception as e:
            print e

        pictures = re.findall(re4, page)
        for picture in pictures:
            try:
                generation = re.search(re5, picture[1]).group(1)
                print picture[0]
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
                sleep(3)
            except Exception as e:
                print e


'''page=open_url(SiteUrl).read()

f=open('models.txt','r').readlines()

re1='<div style="float:right;margin-bottom:1em">([^<]*?)<'
re2='<h2 class="carCaption">(.*?)</h2>.*?<ul class="car-pictures"><li><a href="([^"]*?)">'
re3='<a href="(/pictures/[^"]*?)">'
re4='<a href="([^"]*?)">следующая[^<]*?</a>'
re5='<a href="([^"]*?)">[^<]*?предыдущая</a>'
re6='<strong style="font-size:20px;margin:0 3px">([^<]*?)<'

k=0

for model in f:
    a=0
    print model.strip()

    if k>500:
        # Change IP in Tor
        print "Renewing tor route wait a bit for 5 seconds"
        conn = TorCtl.connect(passphrase="lol")
        conn.sendAndRecv('signal newnym\r\n')
        conn.close()
        import time
        time.sleep(5)
        print "IP changed"
        k=0

    while 1:
        try:
            a+=1
            print a
            page=open_url(model.strip()+'page'+str(a)+'/').read()
            if a==1:
               model_name=re.search(re1,page)
               model_name=model_name.group(1).strip()
               os.makedirs(model_name)
            cars=re.findall(re2,page)
            for car in cars:
                print car[0].replace('<span class="month">','').replace('</span>','').decode('utf-8').encode('cp866','ignore')
                os.mkdir(model_name+'//'+car[0].replace('<span class="month">','').replace('</span>','').strip().decode('utf-8').encode('cp1251'))
                page2=open_url(SiteUrl[:-1]+car[1]).read()
                page3=page2
                pic=re.search(re3,page2)
                number=re.search(re6,page2)
                if number:
                    open(model_name+'//'+car[0].replace('<span class="month">','').replace('</span>','').strip().decode('utf-8').encode('cp1251')+'//'+str(number.group(1))+'.jpg','wb+').write(open_url(SiteUrl[:-1]+pic.group(1)).read())
                else:
                    open(model_name+'//'+car[0].replace('<span class="month">','').replace('</span>','').strip().decode('utf-8').encode('cp1251')+'//'+'1.jpg','wb+').write(open_url(SiteUrl[:-1]+pic.group(1)).read())
                k+=1
                while 1:
                    try:
                        link=re.search(re4,page2)
                        print SiteUrl[:-1]+link.group(1)
                        page2=open_url(SiteUrl[:-1]+link.group(1)).read()
                        pic=re.search(re3,page2)
                        number=re.search(re6,page2)
                        open(model_name+'//'+car[0].replace('<span class="month">','').replace('</span>','').strip().decode('utf-8').encode('cp1251')+'//'+str(number.group(1))+'.jpg','wb+').write(open_url(SiteUrl[:-1]+pic.group(1)).read())
                        k+=1
                    except Exception,e:
                        break
                page2=page3
                while 1:
                    try:
                        link=re.search(re5,page2)
                        print SiteUrl[:-1]+link.group(1)
                        page2=open_url(SiteUrl[:-1]+link.group(1)).read()
                        pic=re.search(re3,page2)
                        number=re.search(re6,page2)
                        open(model_name+'//'+car[0].replace('<span class="month">','').replace('</span>','').strip().decode('utf-8').encode('cp1251')+'//'+str(number.group(1))+'.jpg','wb+').write(open_url(SiteUrl[:-1]+pic.group(1)).read())
                        k+=1
                    except Exception,e:
                        break
        except Exception,e:
            print str(e).decode('cp1251').encode('cp866')
            break
'''