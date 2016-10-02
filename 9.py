from flask import Flask,url_for,request,json,jsonify
from telegram.ext import Updater,CommandHandler
from flaskext.mysql import MySQL
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyMarkup,Update,CallbackQuery,update
import requests,telegram
app = Flask(__name__)
mysql=MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'proj'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)
mysql.connect().autocommit(True)
token="213032540:AAEo6Jidn1uiB_7SI4Papiyh381ORSJR6UE"
bot=telegram.Bot(token)
@app.route('/213032540:AAEo6Jidn1uiB_7SI4Papiyh381ORSJR6UE/webhook',methods=['get','post'])
def token():
	content=request.json
	fname=content['message']['chat']['first_name']
	lname=content['message']['chat']['last_name']
	msg = content['message']['text']
	chat_id=str(content['message']['chat']['id'])
	if msg=='/start':
		str1="welcome "+fname+" "+lname+" please work5"
		keyboard = [[InlineKeyboardButton("Choose Subjects", callback_data='1')],[InlineKeyboardButton("Mock-test", callback_data='2')],[InlineKeyboardButton("Take a random quiz", callback_data='3')],[InlineKeyboardButton("Performance", callback_data='4')],]
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.sendMessage(chat_id=chat_id, text=str1,reply_markup= reply_markup)		
	query = update.callback_query()
	bot.editMessageText(text="Selected option: %s" % query.data,chat_id=query.message.chat_id,message_id=query.message.message_id)
	return jsonify(content)

if __name__ == "__main__":
    app.run(debug=True)
