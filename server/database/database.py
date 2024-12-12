import server.database.models as models
from server.database.data import Device, Metric, Metric_Type

from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
load_dotenv()

class Database:
    def __init__(self, logger, env_var):
        #connect to db
        self.logger = logger
        self.logger.info(f"Connecting to database: {env_var}")
        self.engine = create_engine(os.getenv(env_var))
        self.Session = sessionmaker(bind=self.engine) 

    def create_tables(self):
        from server.database.models import Base  # Import Base where your models are defined
        self.logger.info("Creating all tables...")
        Base.metadata.create_all(self.engine)
        self.logger.info("All tables created successfully.")

    def upload_metrics(self, data, send_time, time_offset):
        session = self.Session()
        try:
            for device in data:
                self.logger.info(f"Uploading data for device: {device['name']}")
                deivce_id = self.check_devices(session, device["guid"], device["name"])

                for metric_type in device["metrics"]:
                    self.logger.info(f"Uploading metric type: {metric_type['metric_type']}")
                    metric_type_id = self.check_metric_type(session, metric_type["metric_type"], metric_type["unit"])

                    for metric in metric_type["values"]:
                        self.logger.info(f"Uploading metric: {metric['value']}")
                        time_id = self.make_time_instance(session, metric["sampled_time"], send_time, time_offset)
                        metric_id = self.make_metric(session, metric["value"], metric_type_id, deivce_id, time_id)
            
            session.commit()  
        except Exception as e:
            session.rollback()  
            raise e
        finally:
            session.close() 


    def make_metric(self, session, value, metric_type_id, device_id, time_id):
        metric = models.Metric(
            value=value, 
            metric_id=metric_type_id, 
            device_id=device_id, 
            time_id=time_id
        )

        session.add(metric)

    def check_devices(self, session, guid, name):
        device = session.query(models.Device).filter_by(id=guid).first()
        if not device:
            device = models.Device(
                id=guid, 
                name=name
            )
            session.add(device)
            session.flush() 
        return device.id
    
    def get_devices(self):
        session = self.Session()
        devices = session.query(models.Device).all()
        parsed_devices = [Device(device.name, device.id) for device in devices]
        session.close()
        return parsed_devices



    def check_metric_type(self, session, name, unit):
        metric_type = session.query(models.Metric_Type).filter_by(name=name, unit=unit).first()
        if not metric_type:
            metric_type = models.Metric_Type(
                name=name, 
                unit=unit
            )
            session.add(metric_type)
            session.flush()  # Flush to get the generated ID
        return metric_type.id

    def get_metric_types(self, session):
        metric_types = session.query(models.Metric_Type).all()
        parsed_metric_types = [Metric_Type(metric_type.name, metric_type.unit) for metric_type in metric_types]
        return parsed_metric_types
    
    def make_time_instance(self, session, sampled_time, sender_time, time_offset):
        now = datetime.now(timezone.utc)
        time_instance = models.Times(
            samples_utc=sampled_time,
            sent_utc=sender_time, 
            samples_min=time_offset, 
            sent_min=time_offset, 
            received_utc=int(now.timestamp()), 
            received_min=int(now.astimezone().utcoffset().total_seconds() / 60)
        )
        session.add(time_instance)
        session.flush() 
        return time_instance.id


    def get_data(self, device_id=None, metric_type_id=None, start_time=None, end_time=None):
        session = self.Session()
        try:
            query = session.query(models.Metric)

            if device_id:
                query = query.filter(models.Metric.device_id == device_id)
            if metric_type_id:
                query = query.filter(models.Metric.metric_id == metric_type_id)
            if start_time:
                query = query.filter(models.Metric.time_id >= start_time)
            if end_time:
                query = query.filter(models.Metric.time_id <= end_time)

            results = query.all()
            return results
        except Exception as e:
            self.logger.error(f"Error retrieving data: {e}")
            raise e
        finally:
            session.close()