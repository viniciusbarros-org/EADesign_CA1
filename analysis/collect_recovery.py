import sys
import os
sys.path.insert(0, "./vendor")
import requests
from datetime import datetime
import time
import MySQLdb
import json
import subprocess
import dateutil.parser

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
        
        command = f"kubectl delete pod -l app={appLabel} --now --wait=false"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.log(output)
        start_time = time.time()
        time.sleep(0.1)

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

        time_to_startup = self.get_startup_time(appLabel)

        self.log(f"End of test downtime of -> {downtime_duration_ms} ms")

        self.save_results(app, appLabel, back, downtime, downtime_duration_ms, time_to_startup)

    def get_startup_time(self, appLabel):
        
        ready = False
        while (not ready):
            command = f"kubectl get pod  -l app={appLabel} --field-selector=status.phase=Running -o json"
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            pod = json.loads(output)

            try:
                start = dateutil.parser.parse(pod['items'][0]['status']['startTime'])
                finish = dateutil.parser.parse(pod['items'][0]['status']['containerStatuses'][0]['state']['running']['startedAt'])
                startup_time = finish - start
                ready = True
            except Exception as e:
                self.log("Info from pod not ready yet. Sleeping for 1 sec")
                time.sleep(1)
        
        
        return(startup_time.seconds * 1000)

    def save_results(self, app, appLabel, back, downtime, downtime_duration, time_to_startup):
        self.log(f"Saving results to DB")
        self.db_c.executemany(
            # Change table name according to tests being performed.
            """INSERT INTO recovery (application, app_down, downtime, recovery_time_ms, time_to_startup)
            VALUES (%s, %s, %s, %s, %s)""",
            [(app, appLabel, downtime, downtime_duration, time_to_startup)]
        )
        self.db.commit()

    def log(self, msg):
        self.logs.append(msg)
        print(msg)

    def get_logs(self):
        return self.logs

    def sleep_in_between(self):
        seconds = 30
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
