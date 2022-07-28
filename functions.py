import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import DBconntctor


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