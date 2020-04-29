import sys
sys.path.insert(0, "./vendor")
import requests
from datetime import datetime
import time
import MySQLdb

class Tests:

    DB_HOST = ''
    DB_USER = ''
    DB_PASS = ''
    DB_NAME = ''
    
    URL = {
        'SYNC':'http://192.168.99.100:32025/collect',
        'ASYNC': 'http://192.168.99.100:30865/collect'
    }

    analysis = []
    db = None
    db_c = None

    def __init__(self):
        self.analysis = []
        self.db=MySQLdb.connect(host=self.DB_HOST,db=self.DB_NAME, user=self.DB_USER,passwd=self.DB_PASS)
        self.db_c = self.db.cursor()

        # self.db_c.execute("""SELECT * from requests""")
        # data = self.db.store_result() 
        # print(data.fetch_row(maxrows=100000,how=1))
        # data = self.db_c.fetchall()
        # print(data)
        # exit(1)
        

    def run(self, app:str, number:int=10, async_a_freq=None, async_b_freq=None, async_g_freq=None):
        url = self.URL[app]
        print('--------------------------------------------------------------------------------')
        print(f"Running {number} tests for app {app} in {url}")
        print('--------------------------------------------------------------------------------')
        for i in range(number):
            
            r = requests.get(url)
            
            response_time_ms = round(r.elapsed.total_seconds() * 1000)

            data = (
                app,
                r.status_code,
                response_time_ms,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                async_a_freq,
                async_b_freq,
                async_g_freq
            )
            self.analysis.append(data)
            print(f"End of test {i+1} -> {response_time_ms} ms")

        self.save_results()

    def save_results(self):
        print(f"Saving {len(self.analysis)} results to DB")
        self.db_c.executemany(
            """INSERT INTO requests (application, status_code, response_time_ms, exec_datetime, async_a_push_freq, async_b_push_freq, async_g_push_freq)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            self.analysis 
        )
        self.db.commit()
        self.analysis = []



tests = Tests()
tests.run('SYNC', 10)
tests.run('ASYNC', 10, 1, 1, 1)


