from flask import Flask
from flask import redirect
from flask import render_template
import flask
import mysql.connector


dns = {'user': 'mysql','host': 'localhost','password': '1','database': 'kaggle'}
connector_toDB = mysql.connector.connect(**dns)
connector_toDB.ping(reconnect=True)

app = Flask(__name__)

Login_users = {"exampleip01ip":"example01user"}

def CheckLogin(ipadress):
    if ipadress in Login_users.keys():
        return True
    return False

def GetUserNameFromIp(ipaderess):
    return Login_users[ipaderess]

def LogoutFromUser(ipadress):
    try:
        Login_users.pop(ipadress)
    except:
        return
    return

def CheckSignin(username,password,ipadress):
    try:
        stmt = 'SELECT passWord FROM users WHERE name = %s'
        cur = connector_toDB.cursor()
        param = (username,)
        cur.execute(stmt,param)
        truePass = cur.fetchall()
        cur.close()
        if password == truePass[0][0]:
            Login_users.setdefault(ipadress,username)
            return True
        return False
    except:
        return False

@app.route('/',methods =['GET','POST'])
def main():
    if flask.request.method == "GET":
        props = {'title': 'Index', 'msg': 'Welcome to Message Center'}
        return render_template('index.html', props=props)
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        print(username + " and " + password + "has detected")
        if CheckSignin(username,password,flask.request.remote_addr) == True:
            return redirect('/message/home')
        props = {'title': 'Index', 'msg': 'Username or PassWord wrong'}
        return render_template('index.html', props=props)

@app.route('/signup', methods=["POST","GET"])
def signup():
    if flask.request.method == "POST":
        username = flask.request.form['username']
        password = flask.request.form['password']
        stmt = 'INSERT INTO users (name,passWord) VALUE ("{}","{}")'.format(username,password)
        cur = connector_toDB.cursor(buffered=True)
        cur.execute(stmt)
        connector_toDB.commit()
        cur.close()
        return redirect('/')
    if flask.request.method == "GET":
        return render_template('signup.html',props = "sign up")

@app.route('/logout',methods = ["GET"])
def logout():
    userip = flask.request.remote_addr
    LogoutFromUser(userip)
    return redirect('/')

@app.route('/message/home', methods = ["GET"])
def msghome():
    if CheckLogin(flask.request.remote_addr) == False:
        redirect('/')
    username = GetUserNameFromIp(flask.request.remote_addr)
    props = {'title': 'message center', 'msg': 'Message Center'}
    return render_template('msghome.html', props=props ,username = username)


@app.route("/message/post", methods=["POST"])
def reciece_msg():
    if CheckLogin(flask.request.remote_addr) == False:
        return redirect('/')
    username = GetUserNameFromIp(flask.request.remote_addr)
    content = flask.request.form["content"]
    postTo = flask.request.form["postTo"]
    stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(username,postTo,content)
    cur = connector_toDB.cursor(buffered=True)
    cur.execute(stmt)
    connector_toDB.commit()
    cur.close()
    return render_template('resultSend.html', postTo = postTo,messageContent = content)

@app.route("/message/get", methods=["POST"])
def get_msg():
    if CheckLogin(flask.request.remote_addr) == False:
        redirect('/')
    username = GetUserNameFromIp(flask.request.remote_addr)
    postFrom = flask.request.form["postFrom"]
    stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
    cur = connector_toDB.cursor()
    param = (postFrom,username,username,postFrom)
    cur.execute(stmt,param)
    Messages = cur.fetchall()
    cur.close()
    return render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages)


if __name__ == '__main__':
    app.run(debug=True)