import mysql.connector

dns = {'user':'root','port':'33306','host': 'localhost','password': 'mysql_pass','database': 'kaggle'}
connector_toDB = mysql.connector.connect(**dns)
connector_toDB.ping(reconnect=True)

def Insert_to_DB(stmt):
    cur = connector_toDB.cursor(buffered=True)
    cur.execute(stmt)
    connector_toDB.commit()
    cur.close()

def Select_from_DB(stmt,param):
    cur = connector_toDB.cursor()
    cur.execute(stmt,param)
    messages = cur.fetchall()
    cur.close()
    return messages