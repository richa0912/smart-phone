from flask import Flask,url_for,request,json,jsonify
from flaskext.mysql import MySQL
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyMarkup,Update,CallbackQuery
import requests,telegram
app = Flask(__name__)
mysql=MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'proj'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)
mysql.connect().autocommit(True)
token="289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ"
bot=telegram.Bot(token)
@app.route('/289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ/webhook',methods=['get','post'])
def token():
	content=request.json
	print content
	if "update_id" in content:
		call(content)
	else:
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		msg = content['message']['text']
		chat_id=str(content['message']['chat']['id'])
		if msg=='/start':
			str1="welcome "+fname+" "+lname
			keyboard = [[InlineKeyboardButton("Choose Subjects", callback_data='01')],[InlineKeyboardButton("Mock-test", callback_data='02')],[InlineKeyboardButton("Take a random quiz", callback_data='03')],[InlineKeyboardButton("Performance", callback_data='04')]]		
			reply_markup = InlineKeyboardMarkup(keyboard)
			bot.sendMessage(chat_id=chat_id, text=str1,reply_markup= reply_markup)
		return jsonify(content)

def call(content):
	if content['callback_query']['data']=='01':
		ch=content['callback_query']['data']
		keyboard = [[InlineKeyboardButton("ds", callback_data='11')],[InlineKeyboardButton("algo", callback_data='12')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.sendMessage(chat_id=chat_id, text="hey "+ fname +" you selected "+ch,reply_markup=reply_markup)
		#bot.answerCallbackQuery(callback_query_id=callback_query.id ,text="you selected "+Update.callback_query.data)
#bot.editMessageText(text="Selected option: %s" % query.data,chat_id=query.message.chat_id,message_id=query.message.message_id)'''
	
	elif content['callback_query']['data']=='11':
		keyboard = [[InlineKeyboardButton("takequiz", callback_data='21')],[InlineKeyboardButton("full-test", callback_data='22')],[InlineKeyboardButton("basic level", callback_data='23')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		#bot.sendMessage(chat_id=chat_id, text="you selected option ",reply_markup=reply_markup)
		bot.sendPhoto(chat_id=chat_id,photo=open('/home/baaje/Desktop/smart_phone/sm/smart-phone/images.jpeg','rb'),reply_markup=reply_markup)

	elif content['callback_query']['data']=='21':
		ch=content['callback_query']
		bot.answerCallbackQuery(callback_query_id=callback_query.id ,text="you selected "+Update.callback_query.data)
		#bot.editMessageText(text="Selected option: %s " % ch['data'],chat_id=chat_id,message_id=content['message']['message_id'])
	return jsonify(content)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
