from flask import Flask,url_for,request
from flaskext.mysql import MySQL
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
wel=[]
@app.route('/274697834:AAHhDcqLAQ0fosM45R6haddl8U64smE62b4/webhook',methods=['post'])
def token():
	if request.method=='POST':
		global count
		count+=1			
		return str(count)			
	else:
		return "welcome"

@app.route('/')
def index():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT ques from user where qid=1")
	data=cursor.fetchone()
	return str(data)
	
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
	cursor.execute("""INSERT INTO user (qid,ques,ans,pty) VALUES (%s,%s,%s,%s)""",(2,insert,'yes',2))
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
    app.run(debug=True)
