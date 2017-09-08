#coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import time
import os
import urllib

from conf import *
from db import *

class OrderImg():
		
	browser = ''
	
	#订单快照列表
	title_links = {}
	#商品详图列表
	title_img_links = {}
	
	lastOrderTime = ''

	orderInfo = []
	orderName = set()

	def __init__(self):
		print chromedriver_path
		self.browser = webdriver.Chrome(chromedriver_path)
		self.browser.get(login_address)
			
		self.dbm = DBMonitor()
		self.dbm.selectDB('tb')
		self.lastOrderTime = self.dbm.query('select max(ordertime) from order_info')

		time.sleep(5)

		
	def login(self):
		#切换到密码登录
		try:
			is_passwd_mode = self.browser.find_element_by_link_text(u'密码登录')
			is_passwd_mode.click()
			
			self.userPwd()
		except:
			self.userPwd()
		time.sleep(60)

	def userPwd(self):
		#输入用户名密码
		self.browser.find_element_by_name('TPL_username').send_keys(tb_username)
		self.browser.find_element_by_name('TPL_password').send_keys(tb_passwd)
	
		time.sleep(3)
		#登录
		self.browser.find_element_by_id('J_SubmitStatic').click()
		
	def orderList(self):
		#跳转至订单列表
		self.browser.get(order_address)
		#切换至frame
		self.browser.switch_to_frame(self.browser.find_element_by_class_name('layout_iframe-iframe'))
		time.sleep(2)
		
		bs = BeautifulSoup(self.browser.page_source,'html.parser')
		
		#订单日期时间
		lis = bs.select('li div div div span.date.col')
		#订单厂商
		lis_factory = bs.select('li div div div div a.bannerCorp.fd-left')
		#订单详情
		order_tables = bs.select('li div table.orderInfo')
		
		#订单数
		orderCount = len(lis)

		for i in range(orderCount):
			order_datetime = lis[i].string

			if order_datetime <= self.lastOrderTime:
				break

			order_dt = order_datetime[:10]
			order_factory = lis_factory[i].string

			aas = order_tables[i].findAll('a', attrs={'class':'productName'})
			
			_oi = {'ordertime':order_datetime, 'factory':order_factory, 'goodname':''}	
			
			for aa in aas:
				link = aa['href']
				title = order_dt + '/' + aa.string
				print aa.string
				if aa.string not in self.orderName:
					self.orderName.add(aa.string)
					#singleGoodInfo
					_oi['goodname'] = aa.string
					self.orderInfo.append(_oi)	
				print self.orderName

				if title not in self.title_links:
					self.title_links[title] = link
					self.title_img_links[title] = set()
		
		time.sleep(20)

	def snapshot(self):
		for k,v in self.title_links.items():
			self.browser.get(v)	
			bs = BeautifulSoup(self.browser.page_source,'html.parser')
			imgs = bs.find('div',attrs={'class':'content fd-editor'}).findAll('img')
			for img in imgs:
#				print img.get('src')
				self.title_img_links[k].add(img.get('src'))
#			break
			time.sleep(3)
		time.sleep(20)

	def saveImgs(self):
		for k,v in self.title_img_links.items():
			good_path = img_root_path+k
			if not os.path.exists(good_path):
				os.makedirs(good_path)
				i = 0
				for img_url in v:
					urllib.urlretrieve(img_url, good_path + '/%s.jpg' % str(i))	
					i = i + 1
			time.sleep(3)

	def imgFilter(self):
		pass	

	def orderInfoUnified(self):
		for oi in self.orderInfo:
			self.dbm.insert('order_info', oi)		
		self.dbm.commit()
#		self.dbm.close()

	def test(self):
		pass

	def run(self):
		self.login()
		self.orderList()
		self.orderInfoUnified()
		self.snapshot()		
		self.saveImgs()

	def quitBrowser(self):
		self.browser.quit()

if __name__ == '__main__':

	oi = OrderImg()
	oi.run()
	time.sleep(30)
	oi.quitBrowser()
