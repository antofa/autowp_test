#-*- coding: utf8 -*-
import sqlite3

conn1 = sqlite3.connect('autowp_full.db')
cur1 = conn1.cursor()
cur1.execute('select * from car')
car1_dict = {}
for row in cur1.fetchall():
    car1_dict[row[1].encode('utf8')] = row[0]
    
print len(car1_dict.keys())

conn2 = sqlite3.connect('autowp_full_2.db')
cur2 = conn2.cursor()
cur2.execute('select * from car')
car2_dict_inv = {}
c = 0
for row in cur2.fetchall():
    car2_dict_inv[row[0]] = row[1].encode('utf8')
    # first step
    '''if row[1].encode('utf8') not in car1_dict.keys():
        c += 1
        print 'insert', c
        print row[1].encode('cp866', 'ignore')
        cur1.execute("insert into car (name) values ('%s')" % row[1].encode('utf8').replace("'", "''"))
        cur1.fetchone()'''
     
# first step     
#conn1.commit()
        
print len(car2_dict_inv.keys())

cur2.execute('select * from picture')
for row in cur2.fetchall():
    try:
        cur1.execute("insert into picture (id, car_id, url, is_saved) values ('%s', %s, '%s', %s)" % (row[0], car1_dict[car2_dict_inv[row[1]]], row[2], row[3]))
        cur1.fetchone()
    except Exception, e:
        if str(e) != 'column id is not unique':
            print e
    
conn1.commit()
