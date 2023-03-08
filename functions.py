import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import DBconntctor
import time

Login_users = {"exampleip":"exampleuser"}

#現在の時間を取得して返す
def GetTime():
    return datetime.datetime.now()

def hash_pass(password):
    return generate_password_hash(password)

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
        param = (username,)
        truePass = DBconntctor.Select_from_DB(stmt,param)
        if check_password_hash(truePass[0][0], password):
            Login_users.setdefault(ipadress,username)
            return True
        return False
    except:
        return False

def check_friend(requestname,requestedname):
    stmt = 'SELECT approved FROM user_friends WHERE requestId = %s AND requestedId = %s'
    param = (requestname,requestedname)
    result = DBconntctor.Select_from_DB(stmt,param)
    try:
        if result[0][0] == 1:
            return True
        else:
            return False
    except:
        return False

def store_image_to_folder(image,username):
    try:
        now_time = time.dateime.now()
        image.save('static/images/' + username + now_time + '.jpg')
        stmt = 'UPDATE users SET image = %s WHERE name = %s'
        param = (username + now_time + '.jpg',username)
        DBconntctor.Update_DB(stmt,param)
        return True
    except:
        return False