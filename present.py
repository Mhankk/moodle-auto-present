#!/usr/bin/python
# -*- coding: utf-8 -*- 

import requests, time, re, sys, os.path
from furl import furl
from bs4 import BeautifulSoup as bs4
import schedule
import time

sess = requests.Session()
target = "https://skansaba.id/" #moodle_target
usr = "xxxxxx" #username
pwd = "xxxxxx" #password

def banner():
	print("""
..............,,.........
|  （✿ ͡◕ ᴗ◕)つ━━✫・*。	|
|      Tidak Perlu      | Author : FilthyRoot
| Bangun Pagi Onii-chan | Github : @soracyberteam
.........................
""")
def get_token(target):
    r = sess.get(target + "/login/index.php")
    s = bs4(r.text, "html.parser").find("input", attrs={'name': 'logintoken'})
    return s.get("value")

def login_moodle(target, user, passwd,token):
    data = {
        'logintoken': token,
        'username': user,
        'password': passwd,
    }
    r = sess.post(target + "/login/index.php", data = data)
    if re.search("loginerrormessage", r.text) or re.search("Anda belum login.", r.text) or re.search("Invalid login, please try again",r.text):
        return False
    else:
        return True

def get_unix_time():
	return int(time.time())

def get_acara():
	data = []
	r = sess.get(target + "/my/")
	s = bs4(r.text, "html.parser").find_all('div', attrs={'class':'event'})
	for i in s:
		if re.search('attendance', str(i)):
			data.append(str(i))
	return data

token = get_token(target)
def get_presensi_id(x):
	try:
		login_moodle(target, usr, pwd, token)
		r = sess.get(x)
		s = bs4(r.text, "html.parser").find('a', attrs={'class':'card-link'})
		return s.get('href')
	except:
		return("[Check] " + x)
def get_timer():
	ori_stdout = sys.stdout
	if(login_moodle(target, usr, pwd, token)):
		with open('/tmp/__time__.txt', 'w') as f:
			sys.stdout = f
			for i in get_acara():
				x = bs4(i, 'html.parser').find('a').get('href')
				print(x)
			sys.stdout = ori_stdout
			f.close()
def get_sesskey(text):
	s = bs4(text, "html.parser").find("input", attrs={'name': 'sesskey'})
	return(s.get('value'))
def get_sessid(text):
	s = bs4(text, "html.parser").find("input", attrs={'name': 'sessid'})
	return(s.get('value'))
def get_status(text):
	s = bs4(text, "html.parser").find("input", attrs={'type': 'radio', 'name': 'status'})
	return(s.get('value'))
def do_presensi(xx):
	try:
		login_moodle(target, usr, pwd, token)
		r = sess.get(xx)
		s = bs4(r.text, "html.parser").find_all('a')
		for i in s:
			if re.search('attendance.php', str(i)):
				o = sess.get(str(i.get('href')))
				if re.search("fdescription required", o.text):
					print("[*] Submitting Form to Present")
					data = {'sessid': get_sessid(o.text), 'sesskey': get_sesskey(o.text), 'sesskey': get_sesskey(o.text), '_qf__mod_attendance_student_attendance_form': 1, 'mform_isexpanded_id_session': 1, 'status': get_status(o.text), 'submitbutton': 'Simpan+perubahan'}
					p = sess.post(target + "/mod/attendance/attendance.php", data=data, headers={'Referer': str(i.get('href'))})
					print("[*] OK")
		return('[Done] ' + xx)
	except:
		return("[Check] " + xx)

banner()

def job():

#def start():
	if os.path.isfile('/tmp/__time__.txt'):
		print("[!] Timestamp found!")
		f = open('/tmp/__time__.txt', 'r')
		x = f.read()
		print(x)
		act = raw_input('[*] Is this Timestamp valid? (y/n) ')
		if act == "n":
			print("[*] Grabbing Timestamp ...")
			get_timer()
			job()
			#start()
		else:
			login_moodle(target, usr, pwd, token)
			for i in x.split("\n"):
				if i == '': continue
				timey = get_unix_time()
				timex = int(furl(i.replace(target, '')).args['time'])
				pres_id = get_presensi_id(i)
				if timey > timex:
					print(do_presensi(str(pres_id)))
				else:
					while(True):
						if get_unix_time() == int(furl(i.replace(target, '')).args['time']):
							print("")
							print(do_presensi(str(pres_id)))
							#sys.stdout.write("\r[*] " + str(get_unix_time()) + " != " + str(int(furl(i.replace(target, '')).args['time'])))
						elif get_unix_time() + 300 == int(furl(i.replace(target, '')).args['time']):
							print("")
							print(do_presensi(str(pres_id)))
							break
						else:
							sys.stdout.write("\r[*] " + str(get_unix_time()) + " != " + str(int(furl(i.replace(target, '')).args['time'])))

	else:
		print("[*] Timestamp not found")
		print("[*] Grabbing Timestamp ...")
		get_timer()
		job()
		#start()
job()
#start()

print("1 Hour Passed")
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
