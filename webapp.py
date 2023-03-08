from concurrent.futures import thread
from pickle import TRUE
from urllib import request
import flask
from flask_socketio import SocketIO, emit, join_room
import DBconntctor
import functions
import os
import ssl

#テキストチャットの通知に使うルーム（キーがユーザーネームで値がルーム番号）
rooms = dict()
#現在のルーム番号の最大値が格納される
room_no = 0
#グループのテキストチャット用
rooms_group = dict()
room_no_group = 1000
#RTC用
rooms_for_rtc = dict()
room_no_rtc = 2000
app = flask.Flask(__name__)
asyncMode = "threading"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=asyncMode, logger=True, engineio_logger=True)
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain('Python/certificate/cert.pem','Python/certificate/privkey.pem')
Login_users = {"exampleip":"exampleuser"}


###########socketio##############
#section for socketio in text chat
#messages for 1 on 1
@socketio.on('join')
def handle_join(postTo,postFrom):
    print(postTo,postFrom)
    global room_no
    global rooms
    for key in rooms:
        if (key == postFrom) or (key == postTo):
            print(rooms[key])
            join_room(rooms[key])
            emit('send_room_no',rooms[key])
            return 
    room_no = room_no + 1
    rooms[postFrom] = room_no
    rooms[postTo] = room_no
    join_room(room_no)
    emit('send_room_no',room_no)

@socketio.on('send')
def send(postFrom,postTo,content,roomNo):
    stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(postFrom,postTo,content)
    DBconntctor.Insert_to_DB(stmt)
    emit('server response', room=roomNo)

#messages for groups
@socketio.on('join_room')
def handle_join_room(group_id):
    global room_no_group
    global rooms_group
    for key in rooms_group:
        if key == group_id:
            print(rooms_group[key])
            join_room(rooms_group[key])
            emit('send_room_no',rooms_group[key])
            return
    room_no_group = room_no_group + 1
    rooms_group[group_id] = room_no_group
    join_room(rooms_group[group_id])
    emit('send_room_no',room_no_group)

@socketio.on('send_group')
def sendGroup(sendername,groupid,content,roomNo):
    stmt = 'INSERT INTO groups_massages (groupID,content,sendername) VALUE ("{}","{}","{}")'.format(groupid,content,sendername)
    DBconntctor.Insert_to_DB(stmt)
    emit('server response',room=roomNo)
###########socketio end##############

###########socketio signaling###########
#section for webRTC signaling
@socketio.on('connect_rtc')
def handle_rtc_connect(connectFrom,connectTo):
    global room_no_rtc
    global rooms_for_rtc
    if connectFrom not in rooms_for_rtc:
        room_no_rtc = room_no_rtc + 1
        rooms_for_rtc[connectFrom] = room_no_rtc
    if connectTo not in rooms_for_rtc:
        room_no_rtc = room_no_rtc + 1
        rooms_for_rtc[connectTo] = room_no_rtc
    print('connected')
    join_room(rooms_for_rtc[connectFrom])

@socketio.on('offer')
def handle_offer(data,connectTo):
    emit('offer_data', data, room=rooms_for_rtc[connectTo])

@socketio.on('answer')
def handle_answer(data,connectTo):
    emit('answer_data', data, room=rooms_for_rtc[connectTo])

@socketio.on('candidate')
def handle_candidate(data,connectTo):
    emit('candidate_data', data, room=rooms_for_rtc[connectTo])

@socketio.on('share_screen')
def handle_share_screen(connectTo):
    emit('share_screen',room=room_no_rtc[connectTo])
###########socketio signaling end####################


###########show voice chat page###################
@app.route('/voiceChat',methods=['GET'])
def videoChat():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    
    #get username and friend name you wanna to connect
    username = functions.GetUserNameFromIp(flask.request.remote_addr)
    connectTo = flask.request.args.get('connectTo')

    #check if user and connectTo is friend
    if functions.check_friend(username,connectTo) == False:
        return flask.redirect('/')

    return flask.render_template('vc_room.html', connectTo = connectTo, connectFrom = username)

###########show signin page##############
@app.route('/',methods =['GET','POST'])
def main():
    if flask.request.method == "GET":
        props = {'title': 'Index', 'msg': 'MessagingCenter'}
        return flask.render_template('index.html', props=props)
    if flask.request.method == 'POST':
        #ユーザ名とパスワードを確認
        username = flask.request.form['username']
        password = flask.request.form['password']

        #現在のユーザから一旦ログアウト
        userip = flask.request.remote_addr
        functions.LogoutFromUser(userip)
        #ログイン
        if functions.CheckSignin(username,password,flask.request.remote_addr) == True:
            return flask.redirect('/message/home')
        props = {'title': 'Index', 'msg': '入力間違いです'}
        return flask.render_template('index.html', props=props)


###########show signup page##############
@app.route('/signup', methods=["POST","GET"])
def signup():
    if flask.request.method == "POST":
        username = flask.request.form['username']
        password = flask.request.form['password']
        #パスワードをハッシュ化して安全性を向上
        password = functions.hash_pass(password)
        stmt = 'SELECT EXISTS(SELECT * FROM users WHERE name = %s)'
        param = (username,)
        #すでにユーザ名が登録済みか確認
        if DBconntctor.Select_from_DB(stmt,param)[0][0]==1:
            return flask.render_template('signup.html',props = "Username already exists")
        #ユーザをデータベースに登録
        stmt = 'INSERT INTO users (name,passWord) VALUE ("{}","{}")'.format(username,password)
        DBconntctor.Insert_to_DB(stmt)
        #ユーザ情報をデータベースに登録
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


###########show user home page##############
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
    print(friendrequests)
    props = {'title': 'メッセージセンター', 'msg': 'メッセージセンター'}
    return flask.render_template('msghome.html', props=props ,username = username,fromMessages = fromMessages,friendrequests = friendrequests)

###########show message page##############
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

        #フレンドかどうかの判定
        if(functions.check_friend(username,postTo) == False):
            return flask.redirect('/message/home')

        #check if message is empty or space
        if(content == "" or content.isspace()):
            return flask.redirect('/message/get?postFrom={}'.format(postFrom))
        
        #send message to user
        stmt = 'INSERT INTO messages (postFrom,postTo,content) VALUE ("{}","{}","{}")'.format(username,postTo,content)
        DBconntctor.Insert_to_DB(stmt)

        #get messages from user
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)

        return flask.render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages,username = username)
    
    else:
        postTo = flask.request.args.get("postFrom")
        postFrom = postTo

        #フレンドかどうかの判定
        if(functions.check_friend(username,postTo) == False):
            return flask.redirect('/message/home')

        #get messages from user
        stmt = 'SELECT * FROM messages WHERE (postFrom = %s AND postTo = %s) OR (postFrom = %s AND postTo = %s)'
        param = (postFrom,username,username,postFrom)
        Messages = DBconntctor.Select_from_DB(stmt,param)

        return flask.render_template('resultGet.html', postFrom = postFrom,MessageContents = Messages,username = username)


###########show group index page##############
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


###########soute for creating group##############
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


###########show group page##############
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

    #ユーザが実際にグループに属しているかの判定
    print(users)
    for user in users:
        if user[2] == username:
            return flask.render_template('group_show.html',props = "グループ", groupname = groupname,users = users,groupid = groupid,MessageContents = messages, username = username)
    
    return flask.redirect('/group')
    


###########route for sending message to group##############
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


###########route for adding user to group##############
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


###########show edit user info page##############
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
            imgFile = None
            print(birthday)
            if "file" in flask.request.files:
                imgFile = flask.request.files["file"]
                UPLOAD_FOLDER = 'Python/static/image/'
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                imgFile.save(os.path.join(app.config['UPLOAD_FOLDER'], username + ".jpg"))
            stmt = 'SELECT COUNT(id) FROM user_info WHERE userId = %s'
            param = (username,)
            count = DBconntctor.Select_from_DB(stmt,param)
            if count[0][0] > 0:
                #update user info
                if birthday == '':
                    stmt = 'UPDATE user_info SET comment = "{}",twitter = "{}",website = "{}" WHERE userId = "{}"'.format(comment,twitter,website,username)
                    DBconntctor.Insert_to_DB(stmt)
                else:
                    stmt = 'UPDATE user_info SET comment = "{}",birthday = "{}",twitter = "{}",website = "{}" WHERE userId = "{}"'.format(comment,birthday,twitter,website,username)
                    DBconntctor.Insert_to_DB(stmt)
            else:
                #insert user info
                if birthday == '':
                    stmt = 'INSERT INTO user_info (userId,comment,twitter,website) VALUE ("{}","{}","{}","{}")'.format(username,comment,twitter,website)
                    DBconntctor.Insert_to_DB(stmt)
                else:
                    stmt = 'INSERT INTO user_info (userId,comment,birthday,twitter,website) VALUE ("{}","{}","{}","{}","{}")'.format(username,comment,birthday,twitter,website)
                    DBconntctor.Insert_to_DB(stmt)
            return flask.redirect('/userinfo/edit')


###########show user info page##############
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
            friend = functions.check_friend(infoname,username)
            if count[0][0] > 0:
                #get user info
                stmt = 'SELECT * FROM user_info WHERE userId = %s'
                param = (infoname,)
                userinfo = DBconntctor.Select_from_DB(stmt,param)
                print(userinfo)
                return flask.render_template('show_user_info.html',username = username,props = "ユーザープロフィール",userinfo = userinfo,friend = friend)
            else:
                return flask.render_template('/no_user_info.html')


##########route for friend request##########
@app.route("/friend/request",methods = ["GET"])
def friend_request():

    #check if user is logged in
    if functions.CheckLogin(flask.request.remote_addr) == False:
        return flask.redirect('/')
    username = functions.GetUserNameFromIp(flask.request.remote_addr)

    requestname = username
    requestedname = flask.request.args.get("requestedname")

    #check if already requested
    stmt = 'SELECT COUNT(id) FROM user_friends WHERE requestedId = %s AND requestId = %s'
    params = (requestedname,requestname,)
    count = DBconntctor.Select_from_DB(stmt,params)
    if count[0][0] > 0:
        stmt = 'UPDATE user_friends SET requested = "{}" WHERE requestedId = "{}" AND requestId = "{}"'.format(1,requestedname,requestname)
        DBconntctor.Insert_to_DB(stmt)
        return flask.redirect('/message/home')
    #insert friend request
    stmt = 'INSERT INTO user_friends (requestedId,requestId,requested) VALUE ("{}","{}","{}")'.format(requestedname,requestname,1)
    DBconntctor.Insert_to_DB(stmt)
    print(stmt)
    return flask.redirect('/message/home')


##########route for approve friend request##########
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

##########route for reject friend request##########
@app.route("/friend/reject",methods = ["GET"])
def friend_reject():
    
        #check if user is logged in
        if functions.CheckLogin(flask.request.remote_addr) == False:
            return flask.redirect('/')
        username = functions.GetUserNameFromIp(flask.request.remote_addr)
    
        requestedname = username
        requestname = flask.request.args.get("requestid")
    
        #insert friend request
        stmt = 'UPDATE user_friends SET  requested = "{}" WHERE requestedId = "{}" AND requestId = "{}"'.format(0,requestedname,requestname)
        DBconntctor.Insert_to_DB(stmt)
        return flask.redirect('/message/home')


if __name__ == '__main__':
    socketio.run(app,debug=True,host='192.168.0.50',port=443,ssl_context=context)