import sys
import os
sys.path.insert(0, "./vendor")
import requests
from datetime import datetime
import time
import MySQLdb
import json
import subprocess

class DowntimeTests:

    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')
    
    URL = {
        'SYNC':'http://35.205.206.0:5000/collect',
        'ASYNC': 'http://35.241.214.62:5000/collect'
    }

    analysis = []
    db = None
    db_c = None
    logs = []

    def __init__(self):
        self.analysis = []
        self.db=MySQLdb.connect(host=self.DB_HOST,db=self.DB_NAME, user=self.DB_USER,passwd=self.DB_PASS)
        self.db_c = self.db.cursor()


    def run(self, app:str, appLabel=None):

        url = self.URL[app]
        self.log('--------------------------------------------------------------------------------')
        self.log(f"Taking down {app} {appLabel} and testing its recovery time")
        self.log('--------------------------------------------------------------------------------')
        
        command = f"kubectl delete pod -l app={appLabel} --wait=false"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.log(output)
        time.sleep(0.1)
        start_time = time.time()

        back = False
        downtime = False
        retry = 0
        while not back:
            try:
                r = requests.get(url)
            except Exception as e:
                self.log(f"Error in request")
                downtime = True
                continue

            self.log(f"{app} is returning {r.status_code}")

            if(r.status_code != 200):
                downtime = True
                time.sleep(0.1)
            if(r.status_code == 200):
                back = True

        finish_time = time.time()
        downtime_duration_ms = (finish_time - start_time)*1000

        self.log(f"End of test downtime of -> {downtime_duration_ms} ms")

        self.save_results(app, appLabel, back, downtime, downtime_duration_ms)

    def save_results(self, app, appLabel, back, downtime, downtime_duration):
        self.log(f"Saving results to DB")
        self.db_c.executemany(
            # Change table name according to tests being performed.
            """INSERT INTO recovery (application, app_down, downtime, recovery_time_ms)
            VALUES (%s, %s, %s, %s)""",
            [(app, appLabel, downtime, downtime_duration)]
        )
        self.db.commit()

    def log(self, msg):
        self.logs.append(msg)
        print(msg)

    def get_logs(self):
        return self.logs

    def sleep_in_between(self):
        seconds = 15
        self.log(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)

def handler(request):
    tests = DowntimeTests()
    
    tests.run('ASYNC','app-a-async')
    tests.sleep_in_between()
    tests.run('ASYNC','app-b-async')
    tests.sleep_in_between()
    tests.run('ASYNC','app-g-async')
    tests.sleep_in_between()
    tests.run('SYNC','app-a-sync')
    tests.sleep_in_between()
    tests.run('SYNC','app-b-sync')
    tests.sleep_in_between()
    tests.run('SYNC','app-g-sync')






# for local only
handler(None)
