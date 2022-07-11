import flask
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import DBconntctor
import functions
import requests

app = flask.Flask(__name__)

Login_users = {"exampleip":"exampleuser"}



@app.route('/',methods =['GET','POST'])
def main():
    if flask.request.method == "GET":
        props = {'title': 'Index', 'msg': 'メッセージセンター'}
        return flask.render_template('index.html', props=props)
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if functions.CheckSignin(username,password,flask.request.remote_addr) == True:
            return flask.redirect('/message/home')
        props = {'title': 'Index', 'msg': '名前かパスワードが間違っています'}
        return flask.render_template('index.html', props=props)

@app.route('/signup', methods=["POST","GET"])
def signup():
    if flask.request.method == "POST":
        username = flask.request.form['username']
        password = flask.request.form['password']
        password = functions.hash_pass(password)
        stmt = 'SELECT EXISTS(SELECT * FROM users WHERE name = %s)'
        param = (username,)
        if DBconntctor.Select_from_DB(stmt,param)[0][0]==1:
            return flask.render_template('signup.html',props = "Username already exists")
        stmt = 'INSERT INTO users (name,passWord) VALUE ("{}","{}")'.format(username,password)
        DBconntctor.Insert_to_DB(stmt)
        return flask.redirect('/')
    if flask.request.method == "GET":
        return flask.render_template('signup.html',props = "アカウント登録")

@app.route('/logout',methods = ["GET"])
def logout():
    userip = flask.request.remote_addr
    functions.LogoutFromUser(userip)
    return flask.redirect('/')

@app.route('/message/home', methods = ["GET"])
def msghome():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    stmt = 'SELECT DISTINCT postFrom FROM messages WHERE postTo = %s'
    param = (username,)
    fromMessages = DBconntctor.Select_from_DB(stmt,param)
    props = {'title': 'メッセージセンター', 'msg': 'メッセージセンター'}
    return flask.render_template('msghome.html', props=props ,username = username,fromMessages = fromMessages)

@app.route("/message/get", methods=["POST"])
def get_msg():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    try:
        content = flask.request.form["content"]
        postTo = flask.request.form["postTo"]
        postFrom = postTo
        stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(username,postTo,content)
        DBconntctor.Insert_to_DB(stmt)
    except:
        postFrom = flask.request.form["postFrom"]
    stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
    param = (postFrom,username,username,postFrom)
    Messages = DBconntctor.Select_from_DB(stmt,param)
    return flask.render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages)


if __name__ == '__main__':
    app.run(debug=True,host='',port = 5000)
