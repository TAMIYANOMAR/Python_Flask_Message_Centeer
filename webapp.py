from pickle import TRUE
from urllib import request
import flask
import DBconntctor
import functions


app = flask.Flask(__name__)

Login_users = {"exampleip":"exampleuser"}


###########show root page##############
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


###########show signup page##############
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
        stmt = 'INSERT INTO user_info (userId) VALUE ("{}")'.format(username)
        DBconntctor.Insert_to_DB(stmt)
        return flask.redirect('/')
    if flask.request.method == "GET":
        return flask.render_template('signup.html',props = "アカウント登録")


###########log out##############
@app.route('/logout',methods = ["GET"])
def logout():
    userip = flask.request.remote_addr
    functions.LogoutFromUser(userip)
    return flask.redirect('/')


@app.route('/message/home', methods = ["GET"])
def msghome():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    
    #get all friends
    stmt = 'SELECT * FROM user_friends WHERE requestedId = %s AND approved = "1"'
    param = (username,)
    fromMessages = DBconntctor.Select_from_DB(stmt,param)

    #get friend requests
    stmt = 'SELECT * FROM user_friends WHERE requestedId = %s AND requested = "1" AND approved = "0"'
    param = (username,)
    friendrequests = DBconntctor.Select_from_DB(stmt,param)

    props = {'title': 'メッセージセンター', 'msg': 'メッセージセンター'}
    return flask.render_template('msghome.html', props=props ,username = username,fromMessages = fromMessages,friendrequests = friendrequests)


@app.route("/message/get", methods=["POST","GET"])
def get_msg():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #if user is sending message
    if flask.request.method == "POST":
        content = flask.request.form["content"]
        postTo = flask.request.form["postTo"]
        postFrom = postTo

        #send message to user
        stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(username,postTo,content)
        DBconntctor.Insert_to_DB(stmt)

        #get messages from user
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)

        return flask.redirect('/message/get?postFrom={}&MessageContents={}&username={}'.format(postFrom,Messages,username))
    else:
        postTo = flask.request.args.get("postFrom")
        postFrom = postTo

        #get messages from user
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)

        return flask.render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages,username = username)


@app.route("/group",methods = ["GET","POST"])
def group_home():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #if method is get
    if flask.request.method == "GET":
        #get all groups
        stmt = 'SELECT * FROM users_groups WHERE userId = %s'
        param = (username,)
        Groups = DBconntctor.Select_from_DB(stmt,param)

        return flask.render_template('group.html',username = username,props = "グループ作成", fromGroups = Groups)


@app.route("/group/create",methods = ["POST"])
def create_group():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #register group
    groupname = flask.request.form["groupname"]
    stmt = 'Insert INTO group_rooms (name,owner) VALUE ("{}","{}")'.format(groupname,username)
    DBconntctor.Insert_to_DB(stmt)
    stmt = 'SELECT id FROM group_rooms WHERE name = %s AND owner = %s LIMIT 1'
    param = (groupname,username)
    group = DBconntctor.Select_from_DB(stmt,param)
    groupid = group[0][0]
    stmt = 'INSERT INTO users_groups (group_name,userID,groupID) VALUE ("{}","{}","{}")'.format(groupname,username,groupid)
    DBconntctor.Insert_to_DB(stmt)

    return flask.redirect('/group')


@app.route("/group/show",methods = ["get"])
def show_group():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #get all groups
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

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #send message to group
    groupid = flask.request.form["groupid"]
    groupname = flask.request.form["groupname"]
    content = flask.request.form["content"]
    sendername = username
    stmt = 'INSERT INTO groups_massages (groupID,content,sendername) VALUE ("{}","{}","{}")'.format(groupid,content,sendername)
    DBconntctor.Insert_to_DB(stmt)

    return flask.redirect('/group/show?groupid={}&groupname={}'.format(groupid,groupname))


@app.route("/group/adduser",methods = ["POST"])
def add_user_to_group():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    #add user to group
    groupid = flask.request.form["groupid"]
    groupname = flask.request.form["groupname"]
    userid = flask.request.form["added_username"]
    stmt = 'INSERT INTO users_groups (group_name,userID,groupID) VALUE ("{}","{}","{}")'.format(groupname,userid,groupid)
    DBconntctor.Insert_to_DB(stmt)

    return flask.redirect('/group/show?groupid={}&groupname={}'.format(groupid,groupname))


@app.route("/userinfo/edit",methods = ["GET","POST"])
def edit_user_info():
    
        #check if user is logged in
        if functions.CheckLogin(flask.request.remote_addr) == False:
            return flask.redirect('/')
        username = functions.GetUserNameFromIp(flask.request.remote_addr)

        #if method is get
        if flask.request.method == "GET":
            stmt = 'SELECT COUNT(id) FROM user_info WHERE userId = %s'
            param = (username,)
            count = DBconntctor.Select_from_DB(stmt,param)
            if count[0][0] > 0:
                #get user info
                stmt = 'SELECT * FROM user_info WHERE userId = %s'
                param = (username,)
                userinfo = DBconntctor.Select_from_DB(stmt,param)
                #print(userinfo)
                return flask.render_template('edit_user_info.html',username = username,props = "ユーザー情報編集",userinfo = userinfo)
            else:
                print("no user info")
                return flask.render_template('edit_user_info_initial.html',username = username,props = "ユーザー情報編集")
    
        #if method is post
        if flask.request.method == "POST":
            comment = flask.request.form["comment"]
            birthday = flask.request.form["birthday"]
            twitter = flask.request.form["twitter"]
            website = flask.request.form["website"]
            stmt = 'SELECT COUNT(id) FROM user_info WHERE userId = %s'
            param = (username,)
            count = DBconntctor.Select_from_DB(stmt,param)
            if count[0][0] > 0:
                #update user info
                stmt = 'UPDATE user_info SET comment = "{}",birthday = "{}",twitter = "{}",website = "{}" WHERE userId = "{}"'.format(comment,birthday,twitter,website,username)
                DBconntctor.Insert_to_DB(stmt)
            else:
                #insert user info
                stmt = 'INSERT INTO user_info (userId,comment,birthday,twitter,website) VALUE ("{}","{}","{}","{}","{}")'.format(username,comment,birthday,twitter,website)
                DBconntctor.Insert_to_DB(stmt)
            return flask.redirect('/userinfo/edit')


@app.route("/userinfo/show",methods = ["GET"])
def show_user_info():
        
            #check if user is logged in
            if functions.CheckLogin(flask.request.remote_addr) == False:
                return flask.redirect('/')
            username = functions.GetUserNameFromIp(flask.request.remote_addr)

            
            #表示したいユーザーのユーザーIDを取得
            infoname = flask.request.args.get("infoname")
            stmt = 'SELECT COUNT(id) FROM user_info WHERE userId = %s'
            param = (infoname,)
            count = DBconntctor.Select_from_DB(stmt,param)
            if count[0][0] > 0:
                #get user info
                stmt = 'SELECT * FROM user_info WHERE userId = %s'
                param = (infoname,)
                userinfo = DBconntctor.Select_from_DB(stmt,param)
                print(userinfo)
                return flask.render_template('show_user_info.html',username = username,props = "ユーザープロフィール",userinfo = userinfo)
            else:
                return flask.render_template('/no_user_info.html')


@app.route("/friend/request",methods = ["GET"])
def friend_request():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    requestname = username
    requestedname = flask.request.args.get("requestname")

    #insert friend request
    stmt = 'INSERT INTO user_friends (requestedId,requestId,requested) VALUE ("{}","{}","{}")'.format(requestedname,requestname,1)
    DBconntctor.Insert_to_DB(stmt)
    return flask.redirect('/message/home')


@app.route("/friend/approve",methods = ["GET"])
def friend_approve():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    requestedname = username
    requestname = flask.request.args.get("requestid")

    #insert friend request
    stmt = 'UPDATE user_friends SET approved = "{}" WHERE requestedId = "{}" AND requestId = "{}"'.format(1,requestedname,requestname)
    DBconntctor.Insert_to_DB(stmt)
    stmt = 'INSERT INTO user_friends (requestedId,requestId,approved) VALUE ("{}","{}","{}")'.format(requestname,requestedname,1)
    DBconntctor.Insert_to_DB(stmt)
    return flask.redirect('/message/home')



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port = 5000)

    