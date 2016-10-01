from flask import Flask,url_for,request,json,jsonify
from flaskext.mysql import MySQL
import requests
app = Flask(__name__)
mysql=MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'proj'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)
mysql.connect().autocommit(True)
token="274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4"
count=0
@app.route('/289036724:AAHY09oWw0Ohn8-uu7-5Ah0tiY8yWfhPLgQ/webhook',methods=['get','post'])
def token():
		content=request.json
		#parsed_json = json.load(content)
		fname=content['message']['chat']['first_name']
		lname=content['message']['chat']['last_name']
		chat_id=str(content['message']['chat']['id'])
		str1="welcome "+fname+" "+lname
		r = requests.post('https://api.telegram.org/bot274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4/sendMessage?chat_id='+chat_id+'&text='+str1, data = {'chatid':'229720277', 'message': 'please'})
		#print(r)
		return jsonify(content)	

@app.route('/')
def index():
	cursor = mysql.connect().cursor()
	#cursor.execute("SELECT ques from user where qid=1")
	#data=cursor.fetchone()
	return "hello"
	
@app.route('/<id>')
def user(id):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from user where qid="+id)
	data = cursor.fetchone()
	if data is None:
		return "Username or Password is wrong"
	else:
		return "Logged in successfully"

@app.route('/add/<string:insert>')
def add(insert):
	db=mysql.connect()
	cursor=db.cursor()
	cursor.execute("""INSERT INTO user (qid,ques,ans,pty) VALUES (%s,%s,%s,%s)""",(1,insert,'yes',2))
	db.commit()
	return "inserted"
	cursor.close()	

@app.route('/introute/<int:mynum>')
def num(mynum):
	return "number is " +str(mynum)

@app.route('/pathroute/<path:mypath>')
def path(mypath):
	return "command is: " + mypath

if __name__ == "__main__":
    app.run(host='0.0.0.0')
