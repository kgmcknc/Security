


#function to go through sensors in database and create threads for all of them, passing config option and pin etc

#function to kill and join all threads so we can reload and restart the sensors

#thread function to send events back to main queue for processing

import security_threads
import database
import queue

class sensor_class:
   def __init__(self, name="sensor", location = 0, event_type = 0, db_id = 0):
      self.name = name
      self.location = location
      self.event_type = event_type
      self.db_id = db_id

class sensor_thread_class:
   def __init__(self, sensor):
      self.sensor = sensor
      self.thread = security_threads.security_thread_class()
      self.thread_queue = queue.Queue()

def start_sensor_threads(sensor_array):
   for s in sensor_array:
      s.thread.start(sensor_process, s)

def stop_sensor_threads(sensor_array):
   for s in sensor_array:
      s.thread.stop_thread()

def add_sensor(instruction):
   new_sensor = sensor_class()
   if("location" in instruction):
      new_sensor.location = instruction["location"]
   if("event_type" in instruction):
      new_sensor.event_type = instruction["event_type"]
   if("name" in instruction):
      new_sensor.name = instruction["name"]
   new_sensor_dict = vars(new_sensor)
   new_sensor_dict.pop("db_id")
   database.add_db_sensor(new_sensor_dict)

def remove_sensor(instruction):
   database.remove_db_sensor(instruction["db_id"])

def sensor_process(sensor_thread, args):
   sensor = args[0]
   print("Sensor Process Started")
   while (sensor_thread.is_active()):
      while(not sensor.thread_queue.empty()):
         try:
            new_queue_data = sensor.thread_queue.get(block=False)
         except:
            #network queue was empty and timed out
            pass
         else:
            print("got sensor data")
      
      sensor_thread.pause(1)
      print("sensor_thread_here")
