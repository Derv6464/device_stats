import eventlet
eventlet.monkey_patch()


from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from server.database.database import Database

from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_socketio import SocketIO,send, emit
from flask_cors import CORS
import json
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd


class Server:
    def __init__(self):
        self.config = Config_Helper('config.json')
        Logger_Helper.setUp(self.config.get('logs_location'))
        self.logger = Logger_Helper.logger

        self.logger.info('This is an info message')

        self.db = Database(self.logger, self.config.get('server.database.host'))

        self.app = Flask(__name__)
        CORS(self.app,resources={r"/*":{"origins":"*"}})
        self.socketio = SocketIO(self.app,cors_allowed_origins="*")

        self.connected_clients = set()
        self.set_routes()

    def set_routes(self):
        self.app.add_url_rule('/', 'hello', self.hello_world)
        self.app.add_url_rule('/metrics', 'get_metrics', self.get_metrics, methods=['POST', 'GET'])
        self.app.add_url_rule('/upload', 'upload_data', self.upload_data, methods=['POST'])
        self.app.add_url_rule('/live', 'live', self.live)
        self.app.add_url_rule('/send_colours', 'send_colours', self.send_colours, methods=['POST'])

        self.socketio.on_event('message', self.handle_message)
        self.socketio.on_event('upload', self.handle_data)
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)


    def hello_world(self):  
        self.logger.info('Hello, World!')
        return 'Hello, World!'


    def get_metrics(self):
        self.logger.info(f'Getting metrics... {request.method}')
        if request.method == 'POST':
            self.logger.info(f'Getting metrics... {request.form}')
            device, metric = request.form.get('device'), request.form.get('metric')
            values, labels  = self.db.get_data(device, metric)
            df = pd.DataFrame({'values': values, 'time': labels})
            df.sort_values(by='time', inplace=True)
            metric = self.db.get_metric_info(metric)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['time'], y=df['values'], mode='lines+markers', name='Metrics'))
            fig.update_layout(
                title="Device Metrics",
                xaxis_title="Time",
                yaxis_title=f'{metric.name} ({metric.unit})',
                template="plotly_white"
            )

            chart_html = pio.to_html(fig, full_html=False)

        else:
            chart_html = None

        devices = self.db.get_devices()
        metrics = self.db.get_metric_types()
        #self.logger.info(f"Loading chart: {chart_html}")
        return render_template('graphs.html', chart_html=chart_html, devices=devices, metrics=metrics)


    def upload_data(self):
        data = request.get_json()
        json_formatted_str = json.dumps(data, indent=2)
        self.logger.info(json_formatted_str)
        devices = data["devices"]
        send_time = data["send_time"]
        time_offset = data["time_offset"]

        self.db.upload_metrics(devices, send_time, time_offset)

        return jsonify({"message": "Data uploaded successfully"})


    def live(self):
        return render_template('live.html', connected=self.connected_clients)

    def send_colours(self):
        data = request.form.get('color')
        self.socketio.emit('colours', data.lstrip("#"))
        return redirect(url_for('live'))
    
    def handle_message(self, message):
        self.logger.info(f"Message from client: {message}")

    def handle_data(self,data):
        devices = data["devices"]
        send_time = data["send_time"]
        time_offset = data["time_offset"]
        emit('upload',data, broadcast=True)
        self.db.upload_metrics(devices, send_time, time_offset)
        send('got it!')

    def handle_connect(self):
        self.connected_clients.add(request.sid) 
        emit('message', 'Hello from the server!')
        self.logger.info('Client connected')

    def handle_disconnect(self):
        self.connected_clients.discard(request.sid)  
        self.logger.info('Client disconnected')


app = Server().app