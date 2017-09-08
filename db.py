#coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb

from conf import *

class DBMonitor():

	def __init__(self):
		
		try:
			# 打开数据库连接
			self.conn = MySQLdb.connect(db_host,db_user,db_passwd,db_dbname,port=3306,charset="utf8")
			self.cur = self.conn.cursor()

		except MySQLdb.Error as e:
			print "Mysql Error %d: %s" % (e.args[0], e.args[1])

	def __del__(self):
		self.close()		
	
	def selectDB(self, db):
		try:
			self.conn.select_db(db)
		except MySQLdb.Error as e:
			print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		
	def query(self, sql):
		try:
			re = self.cur.execute(sql)
			return re
		except MySQLdb.Error as e:
			print "Mysql Error %s: %s" % (e,sql)
				
	def fetchOne(self):
		re = self.cur.fetchone()
		return re

	def fetchAll(self):
		re = self.cur.fetchall()
		desc = self.cur.description

		rows = []
		
		for r in re:
			_row = {}
			for i in range(len(r)):
				_row[desc[i][0]] = str(r[i])
			rows.append(_row)
#		print rows[0]['goodname']
		return rows

	def insert(self, tablename, data):
		columns = data.keys()
		_prefix = 'INSERT INTO ' + tablename
		_fields = ','.join(columns)
		_values = ','.join(['%s' for i in range(len(columns))])	
		sql = _prefix + ' (' + _fields + ') VALUES (' + _values + ')'
		param = tuple([data[k] for k in columns])
		
		self.cur.execute(sql, param)
	
	def update(self, tablename, data, condition):
		_prefix = 'UPDATE ' + tablename + ' SET '
		_fields = []
		for k,v in data.items():
			_fields.append('{} = "{}"'.format(k,v))
		sql = _prefix + ','.join(_fields) + ' WHERE ' + condition

		self.cur.execute(sql)

	def delete(self, tablename, condition):
		_prefix = 'DELETE FROM ' + tablename + ' WHERE '
		sql = _prefix + condition
		self.cur.execute(sql)

	def commit(self):
		self.conn.commit()

	def close(self):
		self.cur.close()
		self.conn.close()

if __name__ == '__main__':
	dbm = DBMonitor()
	dbm.selectDB('tb')
#	dbm.query('select * from order_info')
#	dbm.fetchAll()
	d = {'goodname': '日常', 'ordertime': '2017-03-13 00:11:23'}
	dbm.insert('order_info', d)
	dbm.delete('order_info', 'id = 3')
	dbm.update('order_info', d, 'id = 5')
	dbm.commit()
