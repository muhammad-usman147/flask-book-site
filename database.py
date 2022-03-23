import pymysql 

class Database():
    def __init__(self,dbname,host = 'localhost',user = 'root', pwd = ''):
        self.conn =  pymysql.connect(host =host, user = user, password = pwd)
        self.dbname = dbname

    def createdb(self):
        print("Creating Database: {}".format(self.dbname))
        self.conn.cursor().execute(f'create database {self.dbname}')
        print("DataBase Created Successfully")

    def createTable(self, querystring):
        print(f"RUNNING: {querystring}")
        self.conn.cursor().execute(querystring)
        print(f"Table Created  Successfully")

        

    

    
