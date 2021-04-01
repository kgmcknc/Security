
#function to sound alarm. give type, location, length

#function to stop alarm

# make this a thread and have a queue and then it'll just receive instructions from the queue.
# Main can have array of threads
# Main will kill all threads and restart all alarms and sensors whenenever a sensor/alarm is added or removed

import security_threads
import database
import queue

class alarm_class:
   def __init__(self, name="alarm", location = 0, event_type = 0, db_id = 0):
      self.name = name
      self.location = location
      self.event_type = event_type
      self.db_id = db_id

class alarm_thread_class:
   def __init__(self, alarm):
      self.alarm = alarm
      self.thread = security_threads.security_thread_class()
      self.thread_queue = queue.Queue()

def start_alarm_threads(alarm_array):
   for a in alarm_array:
      a.thread.start(alarm_process, a)

def stop_alarm_threads(alarm_array):
   for a in alarm_array:
      a.thread.stop_thread()

def add_alarm(instruction):
   new_alarm = alarm_class()
   if("location" in instruction):
      new_alarm.location = instruction["location"]
   if("event_type" in instruction):
      new_alarm.event_type = instruction["event_type"]
   if("name" in instruction):
      new_alarm.name = instruction["name"]
   new_alarm_dict = vars(new_alarm)
   new_alarm_dict.pop("db_id")
   database.add_db_alarm(new_alarm_dict)

def remove_alarm(instruction):
   database.remove_db_alarm(instruction["db_id"])

def alarm_process(alarm_thread, args):
   alarm = args[0]
   print("Alarm Process Started")
   while (alarm_thread.is_active()):
      while(not alarm.thread_queue.empty()):
         try:
            new_queue_data = alarm.thread_queue.get(block=False)
         except:
            #network queue was empty and timed out
            pass
         else:
            print("got sensor data")
      
      alarm_thread.pause(1)
      print("alarm_thread_here")