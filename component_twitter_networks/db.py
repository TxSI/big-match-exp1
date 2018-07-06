from pymongo import MongoClient
import config

class DB:
    def __init__(self):
        self.db_host = config.db_host
        self.db_port = config.db_port
        self.db_name = config.db_name
        
        self.connect()
        self.useDB()

    def connect(self):
        self.client = MongoClient(self.db_host, self.db_port)
        if self.client is None:
            print('Cannot connect to the database, please check the host and port in config.py')
        else:
            print('Connected')


    # by default, it will connect to the db_name in config.py
    def useDB(self,db_name = config.db_name):
        self.db_name = db_name
        self.db = self.client[self.db_name]

        print('use database: {}'.format(self.db_name))

    def close(self):
        self.client.close()
        print('Disconnected')
