
import pymongo
import json
import bson

security_db = 0

def exists():
   db_client = pymongo.MongoClient("mongodb://localhost:27017/")
   try:
      dblist = db_client.list_database_names()
   except:
      dblist = db_client.database_names()
   if ("security_db" in dblist):
      return 1
   else:
      return 0

def open_security_db():
   global security_db
   db_client = pymongo.MongoClient("mongodb://localhost:27017/")
   security_db = db_client["security_db"]

def init_security_db():
   global security_db
   print("Initializing Security Database")
   db_client = pymongo.MongoClient("mongodb://localhost:27017/")
   security_db = db_client["security_db"]
   init_config()

def init_config():
   security_config = security_db["config"]
   config_init = {
      "poll_period_ms": 1000,
      "web_port": 60000,
      "armed": 0
      }
   config_info = security_config_class(**config_init)
   security_config.insert_one(vars(config_info))

def get_db_config():
   config_db = security_db["config"]
   security_config_db = config_db.find_one()
   config_data_class = security_config_class(**security_config_db)
   return config_data_class

def set_db_config(config_data):
   config_db = security_db["config"]
   config_query = {}
   config_vars = vars(config_data)
   new_config = {"$set": config_vars}
   config_db.find_one_and_update(config_query, new_config)

def get_db_sensors():
   sensor_list = []
   this_list = security_db.list_collection_names()
   if("sensors" in this_list):
      sensor_db = security_db["sensors"]
      sensor_db_list = sensor_db.find()
      for sensors in sensor_db_list:
         sensors["_id"] = str(sensors["_id"])
         sensor_list.append(sensors)
      return sensor_list
   else:
      return []

def add_db_sensor(new_sensor):
   sensor_db = security_db["sensors"]
   added_sensor = sensor_db.insert_one(new_sensor)
   return added_sensor

def remove_db_sensor(sensor_id):
   sensor_db = security_db["sensors"]
   query_id = bson.ObjectId(str(sensor_id))
   id_query = {"_id": query_id}
   sensor_db.find_one_and_delete(id_query)

def get_db_alarms():
   alarm_list = []
   this_list = security_db.list_collection_names()
   if("alarms" in this_list):
      alarm_db = security_db["alarms"]
      alarm_db_list = alarm_db.find()
      for alarms in alarm_db_list:
         alarms["_id"] = str(alarms["_id"])
         alarm_list.append(alarms)
      return alarm_list
   else:
      return []

def add_db_alarms(new_alarm):
   alarm_db = security_db["alarms"]
   added_alarm = alarm_db.insert_one(new_alarm)
   print(added_alarm)
   return added_alarm

def remove_db_alarms(alarm_id):
   alarm_db = security_db["alarms"]
   id_query = {"_id": alarm_id}
   alarm_db.find_one_and_delete(id_query)

class security_config_class:
   armed = 0
   web_port = 60000
   poll_period_ms = 1000

   def __init__(self, **config_info):
      for key in config_info:
         setattr(self, key, config_info[key])

   def update_config_info(self, **config_info):
      for key in config_info:
         setattr(self, key, config_info[key])

   def to_json(self):
      return json.dumps(vars(self))

#database should have config, status, sensors, alarms

#config has poll rate, global system enable (armed), port for web access
#status has global status info?
#sensors have each sensor, each sensor has enabled, sensor triggered, trigger type, location (for gpio info)
#alarms have each alarm, each alarm has enabled, alarm active, alarm type, location (for gpio info)
