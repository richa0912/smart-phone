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
	print content
	if "callback_query" in content:
		chat_id=str(content['callback_query']['message']['chat']['id'])
	
	elif 'location' in content['message']:  #.index(['location']) is not None:
		chat_id=content['message']['chat']['id']
	
	elif 'text' in content['message']:
		chat_id=str(content['message']['chat']['id'])
	
	cursor.execute("select update_id from user where uid=%s",chat_id)
	update_id=cursor.fetchall()
#	print update_id[0][0]
	if cursor.rowcount==0 or int(content['update_id']) > int(update_id[0][0]):
		updateid=content['update_id']	
		if "callback_query" in content:
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
		
			if (t-int(tcheck))>120:
				bot.sendMessgae(chat_id, "It seems your internet is not working properly. Don't worry your current status is saved :)")
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

			location = geolocator.reverse((lati,longi))
			#print location
			adduser(chat_id,0,name,str(location[0]),updateid)

			cursor.execute("select qid from user where uid=%s",str(chat_id))
			q=cursor.fetchall()
			if q[0][0]==0:
				bot.sendMessage(chat_id, text="The quiz is about to start.")
			elif q[0][0]==5:
				bot.sendMessage(chat_id, text="Continuing the same session of quiz... ")


			db.close()
			takeques(int(q[0][0])+1,chat_id)
		


	
		elif 'text' in content['message']:
			fname=content['message']['chat']['first_name']
			lname=content['message']['chat']['last_name']
			name=fname+" "+lname
			msg = content['message']['text']
			start(name,chat_id,msg,updateid)
			db.close()
	#db.close()
	return jsonify(content)

def adduser(uid,stime,uname,location,updateid):
	db=mysql.connect()
	cursor=db.cursor()
	try:
		cursor.execute("""INSERT INTO user (uid,qid,name,stime,etime,location,loc_stat,score,update_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(uid,0,uname,stime,0,"null","null",0,updateid))
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
		cursor.execute("""update user set loc_stat=%s,location=%s,update_id=%s where uid=%s""",(x,location,updateid,uid))
		db.commit()
		db.close()


def takeques(i,chat_id):
	db=mysql.connect()
	cursor=db.cursor()
	if i==5:
		reply_markup = ReplyKeyboardMarkup([[telegram.KeyboardButton('Pleae share your location' , request_location=True)]] ,one_time_keyboard=True,resize_keyboard=True)
		bot.sendMessage(chat_id,'Hey sorry for interrupting! Would you mind sharing your location just to compare you with other people near your area', reply_markup=reply_markup)
	if(i<=10):
		try:
			cursor.execute("INSERT INTO userques (uid,qid,canswer,ganswer,status,qtime) VALUES (%s,%s,%s,%s,%s,%s)",(chat_id,i,0,0,0,0))
			cursor.execute("update user set qid=%s where uid=%s",(i,chat_id))
			db.commit()
			cursor.execute("select question,answer,opta,optb,optc,optd from quesbank where qid=%s",i)
			ques=cursor.fetchall()
			print ques
			#cursor.execute("select opta,optb,optc,optd from quesbank where qid=%s",i)
			#option=cursor.fetchall()
			#print option
	
			if ques[0][4]=='NULL':	#checking numeric or multiple
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
		l=[]
		x=[]
		cursor.execute("update user set etime=%s where uid=%s",(time.time(),chat_id))
		db.commit()
		cursor.execute("select avg(qtime) from userques where chat_id=%s",chat_id)
		avg=str(cursor.fetchall())
		print avg
		cursor.execute("select score from user where uid=%s",chat_id)
		correct=str(cursor.fetchall())
		bot.sendMessage(chat_id, "Completed. Your score: " +correct[0][0]+ " out of 10.\n You took on an average " +avg[0][0]+ ' seconds to do a ques.' )
		
		cursor.execute("select name,score from user order by score desc limit 3")
		glo=cursor.fetchall()
		if cursor.rowcount>0:
			for k in len(data):
				s=glo[k][0]+" "+glo[k][1]+"\n"
				x.append(s)
			bot.sendMessage(chat_id, 'Global Rank. Top 3 players '+x)
		cursor.execute("select location from user where uid=%s",chat_id)
		locat=str(cursor.fetchall())
		cursor.execute("select name,score from user order by score where location=%s",locat)
		data=str(cursor.fetchall())
		#print data
		if cursor.rowcount>0:
			for k in len(data):
				s=data[k][0]+" "+data[k][1]+"\n"
				l.append(s)
			bot.sendMessage(chat_id, 'Local Rank of people near you: '+s)
		cursor.execute("update user set score=default, qid=0, stime=0, etime=0,loc_stat=0 where uid=%s",chat_id)
		cursor.execute("update userques set qid=0, canswer=0, ganswer=0, status=0,qtime=0 where uid=%s",chat_id)
		db.commit()

	
def checkans(i,chat_id,gans):
	db=mysql.connect()
	cursor=db.cursor()
	print chat_id
	cursor.execute("select answer from quesbank where qid=%s",str(i[0][0]))
	cans=cursor.fetchall()
	cursor.execute("select score from user where uid=%s",str(chat_id))
	score=cursor.fetchall()
	if gans==cans[0][0]:
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
	bot.sendMessage(chat_id, status+".\nExplaination- "+exp[0][0])
	db.close()
	
	
	
		
def start(name,chat_id,msg,updateid):
		if msg=='/start':
			stime=time.time()
			st=adduser(chat_id,stime,name,0,updateid)
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
