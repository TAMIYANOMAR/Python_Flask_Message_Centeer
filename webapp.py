import flask
import DBconntctor
import functions


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

@app.route("/message/get", methods=["POST","GET"])
def get_msg():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    if flask.request.method == "POST":
        content = flask.request.form["content"]
        postTo = flask.request.form["postTo"]
        postFrom = postTo
        stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(username,postTo,content)
        DBconntctor.Insert_to_DB(stmt)
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)
        return flask.redirect('/message/get?postFrom={}&MessageContents={}&username={}'.format(postFrom,Messages,username))
    else:
        postTo = flask.request.args.get("postFrom")
        postFrom = postTo
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)
        return flask.render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages,username = username)

@app.route("/group",methods = ["GET","POST"])
def group_home():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    if flask.request.method == "GET":
        stmt = 'SELECT * FROM users_groups WHERE userId = %s'
        param = (username,)
        Groups = DBconntctor.Select_from_DB(stmt,param)
        return flask.render_template('group.html',username = username,props = "グループ作成", fromGroups = Groups)

@app.route("/group/create",methods = ["POST"])
def create_group():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    groupname = flask.request.form["groupname"]
    print(groupname)
    stmt = 'Insert INTO group_rooms (name,owner) VALUE ("{}","{}")'.format(groupname,username)
    DBconntctor.Insert_to_DB(stmt)
    stmt = 'SELECT id FROM group_rooms WHERE name = %s AND owner = %s LIMIT 1'
    param = (groupname,username)
    group = DBconntctor.Select_from_DB(stmt,param)
    groupid = group[0][0]
    print(groupid)
    stmt = 'INSERT INTO users_groups (group_name,userID,groupID) VALUE ("{}","{}","{}")'.format(groupname,username,groupid)
    DBconntctor.Insert_to_DB(stmt)
    return flask.redirect('/group')

@app.route("/group/show",methods = ["get"])
def show_group():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    groupid = flask.request.args.get("groupid")
    groupname = flask.request.args.get("groupname")
    stmt = 'SELECT * FROM groups_massages WHERE groupId = %s'
    param = (groupid,)
    messages = DBconntctor.Select_from_DB(stmt,param)
    stmt = 'SELECT * FROM users_groups WHERE groupID = %s'
    param = (groupid,)
    users = DBconntctor.Select_from_DB(stmt,param)
    return flask.render_template('group_show.html',props = "グループ作成", groupname = groupname,users = users,groupid = groupid,MessageContents = messages, username = username)

@app.route("/group/send",methods = ["POST"])
def send_group():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    groupid = flask.request.form["groupid"]
    groupname = flask.request.form["groupname"]
    content = flask.request.form["content"]
    sendername = username
    stmt = 'INSERT INTO groups_massages (groupID,content,sendername) VALUE ("{}","{}","{}")'.format(groupid,content,sendername)
    DBconntctor.Insert_to_DB(stmt)
    return flask.redirect('/group/show?groupid={}&groupname={}'.format(groupid,groupname))

@app.route("/group/adduser",methods = ["POST"])
def add_user_to_group():
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    groupid = flask.request.form["groupid"]
    groupname = flask.request.form["groupname"]
    userid = flask.request.form["added_username"]
    stmt = 'INSERT INTO users_groups (group_name,userID,groupID) VALUE ("{}","{}","{}")'.format(groupname,userid,groupid)
    DBconntctor.Insert_to_DB(stmt)
    return flask.redirect('/group/show?groupid={}&groupname={}'.format(groupid,groupname))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port = 5000)

    