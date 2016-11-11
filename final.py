from flask import Flask,url_for,request,json,jsonify
from flaskext.mysql import MySQL
from geopy.geocoders import Nominatim,GoogleV3
import time,random
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
token="274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4"
bot=telegram.Bot(token)
i=1
stime=0
etime=0
qtime=0
qt=0
t=0
tcheck=0
location="null"
gans="null"
mov=[]
cans="null"
@app.route('/274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4/webhook',methods=['get','post'])
def token():
	global stime,ans,i,qt,qtime,t,tcheck,location,gans
	stime=int(time.time())
	content=request.json
	#print content
	if i%5==0:
		reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=False,resize_keyboard=True)
		bot.sendMessage(chat_id, 'Sorry for interrupting!'+name, reply_markup=reply_markup)
		
	if "callback_query" in content:
		t=time.time()
		chat_id=str(content['callback_query']['message']['chat']['id'])
		gans=content['callback_query']['data']
		tcheck=content['callback_query']['message']['date']
		qtime=t-tcheck
		if (t-int(tcheck))>10000:
			print "It seems your internet not working properly. Don't worry your current status is saved :)"
		
		checkans(i,chat_id,gans,qtime)
		#print data
		#i=i+1
		firstques(i,chat_id)
		
	elif 'location' in content['message']:  #.index(['location']) is not None:
		longi = content['message']['location']['longitude']
		lati = content['message']['location']['latitude']
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		name=fname+" "+lname
		geolocator = GoogleV3()
		chat_id=content['message']['chat']['id']
		#location = geolocator.reverse("52.509669, 13.376294")
		location = geolocator.reverse((lati,longi))
		sta=adduser(chat_id,name,str(location[0]))
		#print sta
		bot.sendMessage(chat_id=content['message']['chat']['id'], text="The quiz is about to start.")
		firstques(i,chat_id)


	
	elif 'text' in content['message']:
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		name=fname+" "+lname
		msg = content['message']['text']
		chat_id=str(content['message']['chat']['id'])	
		location1(i,name,chat_id,msg)
	return jsonify(content)

def adduser(uid,uname,location):
	global stime;
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("""INSERT INTO user (uid,name,stime,etime,location) VALUES (%s,%s,%s,%s,%s)""",(uid,uname,stime,0,location))
		print "hi\n"
		db.commit()
		return "s"
	except Exception as e:
		cursor.execute("select location from user where uid=%s",str(uid))
		loc=cursor.fetchall()
		if loc==location:
			mov.append("stationary")
		else:
			mov.append("moving")
		cursor.execute("""update user set location=%s,stime=%s where uid=%s""",(location,stime,uid))
		db.commit()
		
		#print(e)
		#pass
		return "f"

def firstques(i,chat_id):
	global cans,qt
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select question from quesbank where qid=%s",str(i))
	ques=cursor.fetchall()
	#print ques
	cursor.execute("select opta,optb,optc,optd from quesbank where qid=%s",str(i))
	option=cursor.fetchall()
	if cans!='A' and cans!='C' and cans!='B' and cans!='D' :					#checking numeric or multiple
		keyboard = [
    ['7', '8', '9'],
    ['4', '5', '6'],
    ['1', '2', '3'],
    ['-', '.', '0']
];
		reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard = True,one_time_keyboard = True)
	#ans=str(ans)+str(chat_id)+str(i)
	else:
		keyboard = [[InlineKeyboardButton(option[0][0], callback_data='A'+str(chat_id)+str(i))],[InlineKeyboardButton(option[0][1], callback_data='B'+str(chat_id)+str(i))],[InlineKeyboardButton(option[0][2], callback_data='C'+str(chat_id)+str(i))],[InlineKeyboardButton(option[0][3], callback_data='D'+str(chat_id)+str(i))] ]
		reply_markup = InlineKeyboardMarkup(keyboard)
	bot.sendMessage(chat_id, text="Ques."+str(i)+" "+ques[0][0], reply_markup=reply_markup)
	qt=time.time()
	
	
def checkans(i,chat_id,gans,qtime):
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select answer from quesbank where qid=%s",str(i))
	cans=cursor.fetchall()
	if gans==cans:
		status='correct'
	else:
		status='incorrect'	
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("INSERT INTO userques (uid,qid,canswer,ganswer,status,qtime) VALUES (%s,%s,%s,%s,%s,%s)",(chat_id,i,cans,gans,status,qtime))
		db.commit()
	except Exception as e:
		pass
	i+=1
	cursor.execute("select exp from quesbank where qid=%s",str(i))
	exp=cursor.fetchall()
	bot.sendMessage(chat_id=chat_id, text=status+"\nExplaination- "+exp)
	
	
	
		
def location1(i,name,chat_id,msg):
		global stime,cans;
		if msg=='/start':
			#print stime
			st=adduser(chat_id,name,0)
			reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=True,resize_keyboard=True)
			bot.sendMessage(chat_id, 'Hey '+name, reply_markup=reply_markup)
		
		elif '/' not in msg:
			cursor.execute("select answer from quesbank where qid=%s",str(i))
			a=cursor.fetchall()
			if msg==a:
				checkans(i,chat_id,a,qtime)
				firstques(i,chat_id)
		#if msg=='/stat':
		

if __name__ == "__main__":
    app.run(debug=True)
