from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from server.database.database import Database

from flask import Flask, request, jsonify, render_template, url_for
import json
import plotly.graph_objs as go
import plotly.io as pio

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

logger.info('This is an info message')

db = Database(logger, config.get('server.database.host'))

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    logger.info('Hello, World!')
    return 'Hello, World!'

@app.route('/data')
def data():
    logger.info('Getting data...')
    data = db.get_data()
    for i in data:
        logger.info(f"{i.device_id}, {i.time_id}, {i.metric_id}, {i.value}")

    return data

@app.route('/metrics', methods=['POST', 'GET'])
def get_metrics():
    logger.info(f'Getting metrics... {request.method}')
    if request.method == 'POST':
        logger.info(f'Getting metrics... {request.form}')
        device, metric = request.form.get('device'), request.form.get('metric')
        print(device, metric)
        values, labels  = db.get_data(device, metric)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=labels, y=values, mode='lines+markers', name='Metrics'))
        fig.update_layout(
            title="Device Metrics",
            xaxis_title="Time",
            yaxis_title="Metric Value",
            template="plotly_white"
        )

        # Convert the Plotly figure to HTML
        chart_html = pio.to_html(fig, full_html=False)

    else:
        chart_html = None

    devices = db.get_devices()
    metrics = db.get_metric_types()
    #logger.info(f"Loading chart: {chart_html}")
    return render_template('graphs.html', chart_html=chart_html, devices=devices, metrics=metrics)


@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.get_json()
    json_formatted_str = json.dumps(data, indent=2)
    logger.info(json_formatted_str)
    devices = data["devices"]
    send_time = data["send_time"]
    time_offset = data["time_offset"]

    db.upload_metrics(devices, send_time, time_offset)
        
    return jsonify({"message": "Data uploaded successfully"})