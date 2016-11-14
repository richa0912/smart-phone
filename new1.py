from flask import Flask,url_for,request,json,jsonify,session
from flaskext.mysql import MySQL
from geopy.geocoders import Nominatim,GoogleV3
import time
from time import strftime
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,ReplyMarkup,Update,CallbackQuery
import requests,telegram
app = Flask(__name__)
mysql=MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)
mysql.connect().autocommit(True)
token="289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ"
bot=telegram.Bot(token)
chat_id="null"
@app.route('/289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ/webhook',methods=['get','post'])
def token():
	global chat_id
	d=[]
	content=request.json
	print content
	if 'callback_query' in content:
		print "why"
		t=time.time()
		chat_id=str(content['callback_query']['message']['chat']['id'])
	elif 'location' in content['message']:
		chat_id=str(content['message']['chat']['id'])
	
	elif 'text' in content['message']:
		chat_id=str(content['message']['chat']['id'])
	print session
	
	for session_list in session:
		d.append(session_list)
	#print d
	print chat_id
	if chat_id in d:
		#print "ho"
		if session[chat_id][1]%5==0:
			reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=False,resize_keyboard=True)
			bot.sendMessage(session[chat_id][0], 'Sorry for interrupting!'+name, reply_markup=reply_markup)		
	
		if "callback_query" in content:
			t=time.time()
			print t
			#print session[chat_id][5]
			session[chat_id][5]=session[chat_id][5]-int(t)
			gans=content['callback_query']['data']
			tcheck=content['callback_query']['message']['date']
			internet_check=t-tcheck
			if (t-int(internet_check))>10000 and session[chat_id][0]%4==0:
				bot.sendMessage(session[chat_id][0], "It seems your internet not working properly. Don't worry your current status is saved:)" )
			checkans(str(gans))
			#print data
			#i=i+1
			giveques()

		elif 'text' in content['message']:
			fname=content['message']['chat']['first_name']
			lname=content['message']['chat']['last_name']
			name=fname+" "+lname
			msg = content['message']['text']
			start(name,msg)
	
		elif 'location' in content['message']:
			longi = content['message']['location']['longitude']
			lati = content['message']['location']['latitude']
			fname=content['message']['chat']['first_name']
			lname=content['message']['chat']['last_name']
			name=fname+" "+lname
			try:
				geolocator = GoogleV3()
				#location = geolocator.reverse("52.509669, 13.376294")
				location = geolocator.reverse((lati,longi))
				adduser(name,str(location[0]))
			except:
				adduser(name,"null")
			
			bot.sendMessage(session[chat_id][0], text="The quiz is about to start.")
			giveques()


	else:
		#print chat_id
		if 'text' in content['message']:
			fname=content['message']['chat']['first_name']
			lname=content['message']['chat']['last_name']
			name=fname+" "+lname
			msg = content['message']['text']
			start(name,msg)

	return jsonify(content)
	
def start(name,msg):
	global chat_id
	if msg=='/start':
		session[chat_id]=[]
		session[chat_id].append(chat_id)	#0.chat_id
		session[chat_id].append(1)	#1.i
		session[chat_id].append(strftime("%Y-%m-%d %H:%M:%S")) #2.stime
		session[chat_id].append([]) #3.motion
		session[chat_id].append(0)	#4.score
		session[chat_id].append(0) # 5.qtime
		adduser(name,0)
		reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=True,resize_keyboard=True)
		bot.sendMessage(session[chat_id][0], 'Hey '+name, reply_markup=reply_markup)
	
	elif msg=='/stat':
		list=[]
		db=mysql.connect()
		cursor=db.cursor()
		cursor.execute("select avg(qtime) from userques where qid=%s",session[chat_id][1])
		avg=str(cursor.fetchall())
		cursor.execute("select score from user where uid=%s",session[chat_id][0])
		correct=str(cursor.fetchall())
		bot.sendMessage(session[chat_id][0], 'Hey'+name+' .Your score: '+correct+'. You took on an average '+avg+' seconds to do a ques.')
		cursor.execute("select location from user where uid=%s",session[chat_id][0])
		locat=str(cursor.fetchall())
		cursor.execute("select name,score from user where location=%s",locat)
		data=str(cursor.fetchall())
		print data
		for i in locat:
			s=data[i][0]+" "+data[i][1]+"\n"
			list.append(s)
		bot.sendMessage(session[chat_id][0], 'Scores(out of 10) of people near you: '+s)
		
		
	
	else:
		checkans(msg)

def adduser(uname,location):
	global chat_id
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("""INSERT INTO user (uid,name,stime,etime,location) VALUES (%s,%s,%s,%s,%s)""",(session[chat_id][0],uname,session[chat_id][2],0,location))
		#print "hi\n"
		db.commit()
		
	except Exception as e:
		cursor.execute("select location from user where uid=%s",session[chat_id][0])
		loc=cursor.fetchall()
		if loc==location:
			session[chat_id][3].append('stationary')	#list of motions
		else:
			session[chat_id][3].append("moving")
		cursor.execute("""update user set location=%s,stime=%s where uid=%s""",(location,session[chat_id][2],session[chat_id][0]))
		db.commit()

def giveques():
	global chat_id
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select question from quesbank where qid=%s",session[chat_id][1])
	ques=cursor.fetchall()
	cursor.execute("select answer from quesbank where qid=%s",session[chat_id][1])
	cans=cursor.fetchall()
	print cans
	cursor.execute("select opta,optb,optc,optd from quesbank where qid=%s",session[chat_id][1])
	option=cursor.fetchall()
	print option
	if option[0][0]=='null' :				#checking numeric or multiple
		keyboard = [
    ['7', '8', '9'],
    ['4', '5', '6'],
    ['1', '2', '3'],
    ['-', '.', '0']
];
		reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard = True,one_time_keyboard = True)
		
	else:
		keyboard = [[InlineKeyboardButton(option[0][0], callback_data='A')],[InlineKeyboardButton(option[0][1], callback_data='B')],[InlineKeyboardButton(option[0][2], callback_data='C')],[InlineKeyboardButton(option[0][3], callback_data='D')] ]
		reply_markup = InlineKeyboardMarkup(keyboard)
	bot.sendMessage(session[chat_id][0], text="Ques."+str(session[chat_id][1])+" "+ques[0][0], reply_markup=reply_markup)
	session[chat_id][5]=time.time()	#5 is the qtime
	
	
def checkans(gans):
	global chat_id
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select answer from quesbank where qid=%s",session[chat_id][1])
	cans=cursor.fetchall()
	print gans
	print cans
	if gans==cans:
		status='correct'
		session[chat_id][4]+=1
	else:
		status='incorrect'	
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("INSERT INTO userques (uid,qid,canswer,ganswer,status,qtime,score) VALUES (%s,%s,%s,%s,%s,%s)",(session[chat_id][0],session[chat_id][1],cans,gans,status,session[chat_id][5],session[chat_id][4]))
		db.commit()
	except Exception as e:
		pass
	cursor.execute("select exp from quesbank where qid=%s",session[chat_id][1])
	exp=cursor.fetchall()
	bot.sendMessage(session[chat_id][0], text=str(status+". Explaination- "+str(exp)))
	session[chat_id][1]+=1


if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/?RT'
    app.run(host='127.0.0.1')
