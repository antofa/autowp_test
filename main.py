import wx
from Frame1 import Frame1
import sqlite3
from time import sleep
from pprint import pprint
import os, sys
from datetime import datetime
import urllib2
from TorCtl import TorCtl
import ConfigParser
import socket


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('main_'+datetime.now().strftime('%Y-%m-%d')+'.log', 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)


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

socket.setdefaulttimeout(300)
proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"} )

opener = urllib2.build_opener()
urllib2.install_opener(opener)

section = 'autowp'
config = ConfigParser.RawConfigParser()
config.readfp(open('settings.ini'))

request_timeout = config.getint(section, 'request_timeout')
repeat_timeout = config.getint(section, 'repeat_timeout')
use_tor = config.getboolean(section, 'use_tor')
logging = config.getboolean(section, 'logging')

if logging == True:
    sys.stdout = Logger()
    
print '\n', datetime.now().ctime(), 'Start'


def DownloadPictures(id, path):
    print '\nStart Downloading'
    try:
        os.makedirs('pictures/%s' % path)
    except:
        pass
        
    error = False

    print 'Car id:', id
    cur.execute('select id, url from picture where car_id = %s and is_saved = 0' % id)

    pics = []
    for row in cur.fetchall():
        pics.append([row[0], row[1]])

    for pic in pics:
        print pic[0]
        img = ''
        try:
            img = open_url(pic[1])
            if img == 'error':
                raise Exception('Bad image file')
        except Exception as e:
            print 'Error with image %s: %s' % (pic[0], e)
            error = True
            continue
            
        open('pictures/%s/%s.jpg' % (path, pic[0]), 'wb').write(img)
        cur.execute("update picture set is_saved = 1 where url = '%s'" % pic[1]).fetchone()
        conn.commit()
    cur.execute("update car set path = '%s' where id = %s" % ('pictures/' + path, id)).fetchone()
    conn.commit()
    print 'Finish'
    return error


class MyFrame(Frame1):
    def Start(self, event):
        error_car_ids = set()
        m_grid1 = self.m_grid1
        table = m_grid1.GetTable()
        n = table.GetNumberRows()
        for i in range(n):
            if table.GetValue(i, 3):
                id = table.GetValue(i, 0)
                path = table.GetValue(i, 2)
                error = DownloadPictures(id, path)
                if error:
                    error_car_ids.append(id)
        if len(error_car_ids) > 0:
            print '\nError with cars:', ', '.join(i for i in sorted(error_car_ids)) 
        self.OnInit()

    def OnInit(self):
        m_grid1 = self.m_grid1

        cur.execute("SELECT distinct c.id, name FROM car c, picture p where p.car_id = c.id and p.is_saved = 0")
        c = 0

        m_grid1.SetColFormatBool(3)
        n_rows = m_grid1.GetTable().GetNumberRows()
        if n_rows > 0:
            m_grid1.DeleteRows(0, n_rows)

        for row in cur.fetchall():
            m_grid1.AppendRows(1)
            table = m_grid1.GetTable()
            for i in range(2):
                table.SetValue(c, i, str(row[i]).decode('utf8'))
            c += 1        


class AutoWPApp(wx.App):
    def OnInit(self):
        self.m_frame = MyFrame(None)

        self.m_frame.OnInit()

        self.m_frame.Show()
        self.SetTopWindow(self.m_frame)
        return True

app = AutoWPApp()
app.MainLoop()
