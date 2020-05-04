import os
import base64
from io import BytesIO
from flask import Flask
from matplotlib.figure import Figure
import matplotlib
import numpy as np
import MySQLdb

app = Flask(__name__)

class Report:
    
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')
    db = None
    db_c = None

    def __init__(self):
        self.analysis = []
        # DB Connection
        self.db=MySQLdb.connect(host=self.DB_HOST,db=self.DB_NAME, user=self.DB_USER,passwd=self.DB_PASS)
        # Setting to use dictionaries instead of tuples (default)
        self.db_c = self.db.cursor(MySQLdb.cursors.DictCursor)


    def label_bars(self, rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    def get_report1(self):
        query = """SELECT application,
                    AVG(response_time_ms) as average,
                    MIN(response_time_ms) as minimum,
                    MAX(response_time_ms) as maximum,
                    COUNT(id) as number_of_requests
                    FROM requests_1vs1
                    GROUP BY application
                    ORDER BY application ASC
                """
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        result_async = data[0]
        result_sync = data[1]

        labels = ['Minimum', 'Average', 'Maximum', ]
        async_data = [result_async['minimum'], result_async['average'], result_async['maximum']]
        sync_data = [result_sync['minimum'], result_sync['average'], result_sync['maximum']]

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars
        fig = Figure()
        ax = fig.subplots()
        rects1 = ax.bar(x - width/2, async_data, width, label='Async')
        rects2 = ax.bar(x + width/2, sync_data, width, label='Sync')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('millisecond (ms)')
        ax.set_title('Mininimum, average and maximum response times for Async and Sync Apps')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        self.label_bars(rects1, ax)
        self.label_bars(rects2, ax)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>", result_async['number_of_requests'], result_sync['number_of_requests']


    def get_report2_g(self):
        query = """SELECT application, 
                    AVG(response_time_ms) as average,
                    count(id) as number_of_requests,
                    async_g_push_freq
                    FROM requests_g
                    GROUP BY async_g_push_freq
                    ORDER BY async_g_push_freq ASC
                """
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        plot_data = []
        freq = []
        response = []
        for item in data:
            # *1000 as we're saving it in seconds
            freq.append(item['async_g_push_freq']*1000)
            response.append(item['average'])

        fig = Figure()
        ax = fig.subplots()
        ax.plot(freq, response)
        ax.plot(freq, response, "ro")
        ax.set_title('Response time based on polling frequency')
        ax.set_ylabel('Response (ms)')
        ax.set_xlabel('Frequency of polling from App G (ms)')
        
        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"


    def get_report2_ab(self):
        query = """SELECT application, 
                    AVG(response_time_ms) as average,
                    count(id) as number_of_requests,
                    async_a_push_freq
                    FROM requests_ab
                    GROUP BY async_a_push_freq
                    ORDER BY async_a_push_freq ASC
                """
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        plot_data = []
        freq = []
        response = []
        for item in data:
            # *1000 as we're saving it in seconds
            freq.append(item['async_a_push_freq']*1000)
            response.append(item['average'])

        fig = Figure()
        ax = fig.subplots()
        ax.plot(freq, response)
        ax.plot(freq, response, "ro")
        ax.set_title('Response time based on publishing frequency')
        ax.set_ylabel('Response (ms)')
        ax.set_xlabel('Frequency of publishing from Apps A and B (ms)')

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"

    def get_report2_abg(self):
        query = """SELECT application, 
                    AVG(response_time_ms) as average,
                    count(id) as number_of_requests,
                    async_g_push_freq
                    FROM requests_g
                    GROUP BY async_g_push_freq
                    ORDER BY async_g_push_freq ASC
                """
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        freq_g = []
        response_g = []
        for item in data:
            # *1000 as we're saving it in seconds
            freq_g.append(item['async_g_push_freq']*1000)
            response_g.append(item['average'])

        query = """SELECT application, 
                    AVG(response_time_ms) as average,
                    count(id) as number_of_requests,
                    async_a_push_freq
                    FROM requests_ab
                    GROUP BY async_a_push_freq
                    ORDER BY async_a_push_freq ASC
                """
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        plot_data = []
        freq = []
        response = []
        for item in data:
            # *1000 as we're saving it in seconds
            freq.append(item['async_a_push_freq']*1000)
            response.append(item['average'])

        fig = Figure() 
        ax = fig.subplots()
        ax.plot(freq, response, label='Publishing Freq')
        ax.plot(freq_g, response_g, label='Polling Freq')

        ax.set_title('Response time based on publishing frequency')
        ax.set_ylabel('Response (ms)')
        ax.set_xlabel('Frequency (ms)')

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"

    def get_report3(self):
        query = """SELECT application, app_down, 
                    ROUND(AVG(recovery_time_ms),2) as recovery_time_ms, 
                    MAX(downtime) as downtime, 
                    ROUND(AVG(time_to_startup),2) as time_to_startup
                    FROM recovery
                    GROUP BY application, app_down
                    ORDER BY application, app_down"""
        self.db_c.execute(query)
        data = self.db_c.fetchall()

        fig = Figure()
        ax = fig.subplots()
        fig.set_constrained_layout_pads(w_pad=6, h_pad=6)

        app = []
        recovery_time = []
        downtime = []
        # Example data
        for item in data:
            app.append(item['application']+'-'+item['app_down'])
            recovery_time.append(item['recovery_time_ms'])
            ax.text(item['recovery_time_ms'] + 1, len(app)-1 , item['recovery_time_ms'], color='blue')
            ax.text(1, len(app)-1 + .25, "start up of " + str(item['time_to_startup']), color='white')
            ax.text(1, len(app)-1, "Caused downtime" if item['downtime'] else '',  color='yellow', fontweight='bold')


        y_pos = np.arange(len(app))

        ax.barh(y_pos, recovery_time)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(app)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Recovery Time in millisecond (ms)')
        ax.set_title('Application Recovery time based on component taken down')


        buf = BytesIO()
        fig.set_tight_layout(True)
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"


@app.route("/")
def index():
    return """
    <body style='text-align:center; background-color:#f1f1f1'>
    <h1>EADesign - Welcome to the reports</h1>

    <ul style='display: block;margin-left: auto;margin-right: auto;width: 500px;text-align: left;'>
    <li><a href="/report1">1 Response time Sync vs Async</a></li>
    <li><a href="/report2">2 Async Response time in function of frequency of events</a></li>
    <li><a href="/report3">3 Recovery time</a></li>
    </ul>
    </body>
    """

@app.route("/report1")
def report1():
    report = Report()

    plot, async_requests, sync_requests = report.get_report1()
    note = "Async Apps A,B and G were all set to pub/sub at a frequency of 0.05 seconds."
    note2 = f"Plot based on the following number of requests: {async_requests} to ASYNC and {sync_requests} to SYNC"
    return f"""
    <html>
    <body style='text-align:center; background-color:#f1f1f1'>
    <h1>Report 1 - Response time Sync vs Async</h1>
    {plot}
    <br/>
    <p>{note}</p>
    <p>{note2}</p>
    <p>Shown data are average of multiple records collected.</p>

    </body>
    </html>
    """

@app.route("/report2")
def report2():
    report = Report()

    plot = report.get_report2_g()
    plot2 = report.get_report2_ab()
    plot3 = report.get_report2_abg()
    note = "Async Apps A and B were publishing at a frequency of 0.05 seconds."
    note2 = "Async App G were polling at a frequency of 0.05 seconds."
    note3 = "Orange line is plot in function of freq from G, and Blue line in function of freq. from A and B."
    return f"""
    <html>
    <body style='text-align:center; background-color:#f1f1f1'>
    <h1>Report 2 - Async - Response in function of the frequency of events</h1>
    <h2>In frequency of Polling from G</h2>
    {plot}
    <p>{note}</p>
    <h2>In frequency of Publishing from A and B</h2>

    {plot2}
    <p>{note2}</p>
    <h2>Both plots side by side</h2>
    {plot3}
    <p>{note3}</p>
    <p>Shown data are average of multiple records collected.</p>


    </body>
    </html>
    """


@app.route("/report3")
def report3():
    report = Report()

    plot = report.get_report3()
    note = """Apps flagged with the yellow text "Caused downtime" were 
    inaccessible while the application was being recovered.
    <br>
    The startup time information inside the bars was extracted from kubernetes by checking
    how long it took since the creation of the pod until it was in ready state.
    """
    

    return f"""
    <html>
    <body style='text-align:center; background-color:#f1f1f1'>
    <h1>Report 3 - Application Recovery times</h1>
    {plot}
    <p>{note}</p>
    <p>Shown data are average of multiple records collected.</p>

    </body>
    </html>
    """

def handler(request):
    return index()

def handler1(request):
    return report1()

def handler2(request):
    return report2()

def handler3(request):
    return report3()


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')