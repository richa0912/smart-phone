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
token="274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4"
bot=telegram.Bot(token)
@app.route('/274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4/webhook',methods=['get','post'])
def token():
	content=request.json
	if 'chat_id' in session:
		if session['i']%5==0:
			reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=False,resize_keyboard=True)
			bot.sendMessage(session['chat_id'], 'Sorry for interrupting!'+name, reply_markup=reply_markup)
			
			
		if "callback_query" in content:
			t=time.time()
			session['qtime']=session['qtime']-t
			gans=content['callback_query']['data']
			tcheck=content['callback_query']['message']['date']
			internet_check=t-tcheck
			if (t-int(internet_check))>10000 and session['i']%4==0:
				bot.sendMessage(session['chat_id'], "It seems your internet not working properly. Don't worry your current status is saved:)" )	
			checkans(str(gans)[0])
			#print data
			#i=i+1
			takeques()
	
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
			geolocator = GoogleV3()
			#location = geolocator.reverse("52.509669, 13.376294")
			location = geolocator.reverse((lati,longi))
			adduser(session['chat_id'],name,str(location[0]))
			bot.sendMessage(session['chat_id'], text="The quiz is about to start.")
			giveques(session['i'],session['chat_id'])
	
	else:
		session['chat_id']=content['message']['chat']['id']
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		name=fname+" "+lname
		msg = content['message']['text']
		start(name,msg)
		
	return jsonify(content)
	
def start(name,msg):
	if msg=='/start':
		session['i']=1
		session['stime']=strftime("%Y-%m-%d %H:%M:%S")
		session['list']=[]
		session['score']=0
		adduser(name,0)
		reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=True,resize_keyboard=True)
		bot.sendMessage(session['chat_id'], 'Hey '+name, reply_markup=reply_markup)
	
	if msg=='/stat':
		db=mysql.connect()
		cursor=db.cursor()
		cursor.execute("select avg(qtime) from userques where qid=%s",session['chat_id'])
		avg=cursor.fetchall()
		cursor.execute("select score from user where uid=%s",session['chat_id'])
		correct=cursor.fetchall()
		bot.sendMessage(session['chat_id'], 'Hey'+name+' .Your score: '+correct'. You took on an average '+avg+' seconds to do a ques.')
		cursor.execute("select location from user where uid=%s",session['chat_id'])
		locat=cursor.fetchall()
		cursor.execute("select name,score from user where location=%s",locat)
		locat=cursor.fetchall()
		bot.sendMessage(session['chat_id'], 'Scores of people near you: '+locat)
		


def adduser(uname,location):
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("""INSERT INTO user (uid,name,stime,etime,location) VALUES (%s,%s,%s,%s,%s)""",(session['chat_id'],uname,session['stime'],0,location))
		#print "hi\n"
		db.commit()
		
	except Exception as e:
		cursor.execute("select location from user where uid=%s",session['chat_id'])
		loc=cursor.fetchall()
		if loc==location:
			session['list'].append('stationary')
		else:
			session['list'].append("moving")
		cursor.execute("""update user set location=%s,stime=%s where uid=%s""",(location,session['stime'],session['chat_id']))
		db.commit()

def giveques():
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select question from quesbank where qid=%s",session['i'])
	ques=cursor.fetchall()
	#print ques
	cursor.execute("select opta,optb,optc,optd from quesbank where qid=%s",session['i'])
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
		keyboard = [[InlineKeyboardButton(option[0][0], callback_data='A')],[InlineKeyboardButton(option[0][1], callback_data='B')],[InlineKeyboardButton(option[0][2], callback_data='C')],[InlineKeyboardButton(option[0][3], callback_data='D')] ]
		reply_markup = InlineKeyboardMarkup(keyboard)
	bot.sendMessage(session['chat_id'], text="Ques."+session['i']+" "+ques[0][0], reply_markup=reply_markup)
	session['qtime']=time.time()
	
	
def checkans(gans):
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("select answer from quesbank where qid=%s",session['i'])
	cans=cursor.fetchall()
	if gans==cans:
		status='correct'
		session['score']+=1
	else:
		status='incorrect'	
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("INSERT INTO userques (uid,qid,canswer,ganswer,status,qtime,score) VALUES (%s,%s,%s,%s,%s,%s)",(session['chat_id'],session['i'],cans,gans,status,session['qtime'],session['score']))
		db.commit()
	except Exception as e:
		pass
	cursor.execute("select exp from quesbank where qid=%s",session['i'])
	exp=cursor.fetchall()
	bot.sendMessage(session['chat_id'], text=str(status+". Explaination- "+str(exp)))
	session['i']+=1


if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/?RT'
    app.run(debug=True)
