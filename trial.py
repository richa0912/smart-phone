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
token="289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ"
bot=telegram.Bot(token)
@app.route('/289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ/webhook',methods=['get','post'])
def token():
	content=request.json
	db=mysql.connect()
	cursor=db.cursor()
	#print content
	'''if i%5==0:
		reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=False,resize_keyboard=True)
		bot.sendMessage(chat_id, 'Sorry for interrupting!'+name, reply_markup=reply_markup)
	'''	
	if "callback_query" in content:
		chat_id=str(content['callback_query']['message']['chat']['id'])
		gans=content['callback_query']['data']
		tcheck=content['callback_query']['message']['date']
		cursor.execute("select qid from user where uid=%s",chat_id)
		i=cursor.fetchall()
		
		cursor.execute("select qtime from userques where qid=%s and uid=%s",(i[0][0],chat_id))
		qtime=cursor.fetchall()
		t=time.time()
		qt=t-qtime[0][0]
		print t
		cursor.execute("update userques set qtime=%s where qid=%s and uid=%s",(qt,i[0][0],chat_id))
		db.commit()
		db.close()
		
		if (t-int(tcheck))>10000:
			print "It seems your internet not working properly. Don't worry your current status is saved :)"
		checkans(i,chat_id,gans)
		#print data
		#i=i+1
		takeques(int(i[0][0])+1,chat_id)
		
	elif 'location' in content['message']:  #.index(['location']) is not None:
		longi = content['message']['location']['longitude']
		lati = content['message']['location']['latitude']
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		name=fname+" "+lname
		geolocator = GoogleV3()
		chat_id=content['message']['chat']['id']

		location = geolocator.reverse((lati,longi))
		#print location
		adduser(chat_id,0,name,str(location[0]))
		bot.sendMessage(chat_id, text="The quiz is about to start.")

		cursor.execute("select qid from user where uid=%s",str(chat_id))
		q=cursor.fetchall()
		db.close()
		takeques(int(q[0][0])+1,chat_id)
		


	
	elif 'text' in content['message']:
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		name=fname+" "+lname
		msg = content['message']['text']
		chat_id=str(content['message']['chat']['id'])
		start(name,chat_id,msg)
		db.close()
	#db.close()
	return jsonify(content)

def adduser(uid,stime,uname,location):
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("""INSERT INTO user (uid,qid,name,stime,etime,location,loc_stat,score) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(uid,0,uname,stime,0,"null","null",0))
		db.commit()
	except Exception as e:
		cursor.execute("select location,loc_stat from user where uid=%s",str(uid))
		loc=cursor.fetchall()
		#x=lstat[0][1].rsplit(",",1)[1]
		if loc[0][0]==location:
			x=loc[0][1]+",stationary"
			print loc[0][1]
#			cursor.execute("""update user set location=%s where uid=%s""",(loc[0],stime,uid))
		else:
			x=loc[0][1]+",moving"
		cursor.execute("""update user set loc_stat=%s,location=%s where uid=%s""",(x,location,uid))
		db.commit()
		db.close()


def takeques(i,chat_id):
	db=mysql.connect()
	cursor=db.cursor()
	if(i<=10):
		try:
			cursor.execute("INSERT INTO userques (uid,qid,canswer,ganswer,status,qtime) VALUES (%s,%s,%s,%s,%s,%s)",(chat_id,i,0,0,0,0))
			cursor.execute("update user set qid=%s where uid=%s",(i,chat_id))
			db.commit()
			cursor.execute("select question,answer,opta,optb,optc,optd from quesbank where qid=%s",i)
			ques=cursor.fetchall()
			print cursor
			#cursor.execute("select opta,optb,optc,optd from quesbank where qid=%s",i)
			#option=cursor.fetchall()
			#print option
	
			if ques[0][3]=='null' :				#checking numeric or multiple
				keyboard = [
		    ['7', '8', '9'],
		    ['4', '5', '6'],
		    ['1', '2', '3'],
		    ['-', '.', '0']
		];
				reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard = True,one_time_keyboard = True)
		
			else:
				keyboard = [[InlineKeyboardButton(ques[0][2], callback_data='A')],[InlineKeyboardButton(ques[0][3], callback_data='B')],[InlineKeyboardButton(ques[0][4], callback_data='C')],[InlineKeyboardButton(ques[0][5], callback_data='D')] ]
				reply_markup = InlineKeyboardMarkup(keyboard)
	
			bot.sendMessage(chat_id, text="Ques."+str(i)+" "+ques[0][0], reply_markup=reply_markup)
	
			cursor.execute("update userques set qtime=%s,canswer=%s where qid=%s and uid=%s",(time.time(),ques[0][1],i,chat_id))
			db.commit()
	
		except Exception as e:
			print e
			#cursor.execute("select qid from user where uid=%s",str(chat_id))
			#q=cursor.fetchall()
			#db.close()
			#takeques(int(q[0][0])+1,chat_id)
	else:
		
		cursor.execute("select avg(qtime) from userques where qid=%s",i)
		avg=str(cursor.fetchall())
		print avg
		cursor.execute("select score from user where uid=%s",chat_id)
		correct=str(cursor.fetchall())
		bot.sendMessage(chat_id, "Completed. Your score: " +correct[0][0]+ ". You took on an average " +avg[0][0]+ ' seconds to do a ques.' )
		cursor.execute("select location from user where uid=%s",chat_id)
		locat=str(cursor.fetchall())
		cursor.execute("select name,score from user where location=%s",locat)
		data=str(cursor.fetchall())
		print data
		for i in data:
			s=data[i][0]+" "+data[i][1]+"\n"
			list.append(s)
		bot.sendMessage(chat_id, 'Scores(out of 10) of people near you: '+s)

	
def checkans(i,chat_id,gans):
	db=mysql.connect()
	cursor=db.cursor()
	print chat_id
	cursor.execute("select answer from quesbank where qid=%s",str(i[0][0]))
	cans=cursor.fetchall()
	cursor.execute("select score from user where uid=%s",str(chat_id))
	score=cursor.fetchall()
	if gans==cans:
		status='Correct'
		cursor.execute("""update user set score=%s where uid=%s""",(int(score[0][0])+1,chat_id))
		db.commit()
	else:
		status='Incorrect'	
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("update userques set canswer=%s,ganswer=%s,status=%s where uid=%s and qid=%s",(cans,gans,status,chat_id,i))
		db.commit()
	except Exception as e:
		pass
	cursor.execute("select exp from quesbank where qid=%s",str(i[0][0]))
	print i
	exp=cursor.fetchall()
	bot.sendMessage(chat_id=chat_id, text=str(status)+"\nExplaination- "+str(exp[0][0]))
	db.close()
	
	
	
		
def start(name,chat_id,msg):
		if msg=='/start':
			stime=time.time()
			st=adduser(chat_id,stime,name,0)
			reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Do you want to share Location', request_location=True)]],one_time_keyboard=True,resize_keyboard=True)
			bot.sendMessage(chat_id, 'Hey '+name, reply_markup=reply_markup)
		
		'''elif '/' not in msg:
			cursor.execute("select answer from quesbank where qid=%s",str(i))
			a=cursor.fetchall()
			if msg==a:
				checkans(i,chat_id,a,qtime)
				firstques(i,chat_id)
		#if msg=='/stat':
		'''

if __name__ == "__main__":
    app.run(host='0.0.0.0')
