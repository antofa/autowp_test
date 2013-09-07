import wx
from Frame1 import Frame1
import sqlite3
from time import sleep
from pprint import pprint
import os
import urllib2

m = ['la', 'lo', 'lu', 'ly', 'le']

# Change "AutoWPApp" with the name of your application

conn = sqlite3.connect('autowp.db', timeout=300)
conn.text_factory = str
cur = conn.cursor()

opener = urllib2.build_opener()
urllib2.install_opener(opener)


def DownloadPictures(id, path):
    print '\nStart Downloading'
    try:
        os.makedirs('pictures/%s' % path)
    except:
        pass

    print 'Generation id:', id
    cur.execute('select id, url from picture where generation_id = %s and is_saved = 0' % id)

    pics = []
    for row in cur.fetchall():
        pics.append([row[0], row[1]])

    for pic in pics:
        print pic[0]
        try:
            open('pictures/%s/%s.jpg' % (path, pic[0]), 'wb').write(opener.open(pic[1]).read())
        except Exception as e:
            print e

        cur.execute("update picture set is_saved = 1 where url = '%s'" % pic[1]).fetchone()
        conn.commit()
    print 'Finish'


class MyFrame(Frame1):
    def Start(self, event):
        m_grid1 = self.m_grid1
        table = m_grid1.GetTable()
        n = table.GetNumberRows()
        for i in range(n):
            if table.GetValue(i, 5):
                id = table.GetValue(i, 0)
                path = table.GetValue(i, 4)
                DownloadPictures(id, path)
        self.OnInit()

    def OnInit(self):
        m_grid1 = self.m_grid1

        cur.execute("SELECT distinct g.id, mark, model, generation FROM generation g, picture p where p.generation_id = g.id and p.is_saved = 0")
        c = 0

        m_grid1.SetColFormatBool(5)
        n_rows = m_grid1.GetTable().GetNumberRows()
        if n_rows > 0:
            m_grid1.DeleteRows(0, n_rows)

        for row in cur.fetchall():
            m_grid1.AppendRows(1)
            table = m_grid1.GetTable()
            for i in range(4):
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
