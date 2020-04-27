import sys
sys.path.insert(0, "./vendor")
import requests
from datetime import datetime
import time

class Tests:
    
    URL = {
        'SYNC':'http://192.168.99.100:32025/collect',
        'ASYNC': 'http://192.168.99.100:30865/collect'
    }

    analysis = []
        

    def run(self, app:str, number:int=10):
        url = self.URL[app]
        print('--------------------------------------------------------------------------------')
        print(f"Running {number} tests for app {app} in {url}")
        print('--------------------------------------------------------------------------------')
        for i in range(number):
            
            r = requests.get(url)
            

            
            response_time_ms = round(r.elapsed.total_seconds() * 1000)

            data = {
                'application': app,
                # 'application': url,
                "status_code" : r.status_code,
                "response_time_ms": response_time_ms
                
            }
            self.analysis.append(data)
            print(f"End of test {i+1} -> {response_time_ms} ms")

        print(self.analysis)



tests = Tests()
tests.run('SYNC', 100)
tests.run('ASYNC', 100)


