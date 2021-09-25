
import global_data
import security_threads
import sensors
import alarms
import database
import threading
import networking
import signal
import sys
import queue
import json

main_thread = security_threads.security_thread_class("Main Security Thread")
network_thread = security_threads.security_thread_class("Network Thread")

system_config = 0
sensor_thread_array = []
alarm_thread_array = []

system_running = 1

def security_main(main_thread):
   global system_config
   global sensor_thread_array
   global alarm_thread_array

   print("Starting Main")

   init_system()

   network_thread.start(networking.network_listener)

   sensors.start_sensor_threads(sensor_thread_array)
   alarms.start_alarm_threads(alarm_thread_array)

   my_ip = networking.get_my_ip()
   my_port = system_config.web_port
   old_ip = my_ip
   old_port = my_port

   print("main while")
   while (main_thread.is_active()):
      my_ip = networking.get_my_ip()
      my_port = system_config.web_port
      if((my_ip != old_ip) or (my_port != old_port)):
         print("Config changed")
         network_thread.stop_thread()
         network_thread.start(networking.network_listener)
         
      try:
         new_main_instruction = global_data.main_queue.get(timeout=global_data.main_queue_timeout)
      except:
         #main queue was empty and timed out
         pass
      else:
         #log whatever we got from queue here...
         process_main_instruction(new_main_instruction)
   
   security_shutdown()
   return

def process_main_instruction(instruction):
   if(instruction.group == "system_tasks"):
      if(instruction.task == "shutdown_delay"):
         while(main_thread.is_active()):
            pass

   if(instruction.group == "sensor_tasks"):
      if(instruction.task == "sensor_triggered"):
         print("sensor triggered")

   if(instruction.group == "alarm_tasks"):
      if(instruction.task == "alarm_on"):
         print("alarm on")
      if(instruction.task == "alarm_of"):
         print("alarm off")

   if(instruction.group == "local_tasks"):
      if(instruction.task == "get"):
         return_data = process_get(instruction)
         instruction.data = return_data
         global_data.network_queue.put(instruction, block=False)
      if(instruction.task == "post"):
         process_post(instruction)

def process_get(instruction):
   json_object = instruction.data
   instruction.data = {}

   if(json_object["command"] == "get_sensors"):
      sensor_list = database.get_db_sensors()
      instruction.data["command"] = "get_sensors"
      instruction.data["sensors"] = sensor_list

   if(json_object["command"] == "get_alarms"):
      alarm_list = database.get_db_alarms()
      instruction.data["command"] = "get_alarms"
      instruction.data["alarms"] = alarm_list

   return instruction.data

def process_post(instruction):
   global sensor_thread_array
   global alarm_thread_array

   sensor_array = []
   alarm_array = []

   restart_sensors = 0
   restart_alarms = 0

   if(instruction.data["command"] == "add_sensor"):
      restart_sensors = 1
      sensors.add_sensor(instruction.data)

   if(instruction.data["command"] == "remove_sensor"):
      restart_sensors = 1
      sensors.remove_sensor(instruction.data)

   if(instruction.data["command"] == "add_alarm"):
      restart_alarms = 1
      alarms.add_alarm(instruction.data)
      
   if(instruction.data["command"] == "remove_alarm"):
      restart_alarms = 1
      alarms.remove_alarm(instruction.data)

   if(restart_sensors):
      sensors.stop_sensor_threads(sensor_thread_array)
      sensor_thread_array = []
      sensor_array = database.get_db_sensors()
      for s in sensor_array:
         new_sensor_thread = sensors.sensor_thread_class(s)
         sensor_thread_array.append(new_sensor_thread)
      sensors.start_sensor_threads(sensor_thread_array)
   
   if(restart_alarms):
      alarms.stop_alarm_threads(alarm_thread_array)
      alarm_thread_array = []
      alarm_array = database.get_db_alarms()
      for a in alarm_array:
         new_alarm_thread = alarms.alarm_thread_class(a)
         alarm_thread_array.append(new_alarm_thread)
      alarms.start_alarm_threads(alarm_thread_array)

def init_system():
   global system_config
   global sensor_thread_array
   global alarm_thread_array

   sensor_array = []
   alarm_array = []

   if(database.exists()):
      database.open_security_db()
   else:
      database.init_security_db()
   
   system_config = database.get_db_config()

   sensor_array = database.get_db_sensors()
   for s in sensor_array:
      new_sensor_thread = sensors.sensor_thread_class(s)
      sensor_thread_array.append(new_sensor_thread)
   
   alarm_array = database.get_db_alarms()
   for a in alarm_array:
      new_alarm_thread = alarms.alarm_thread_class(a)
      alarm_thread_array.append(new_alarm_thread)

def exit_handler(signum, frame):
   global system_running
   if(system_running):
      system_running = 0
      print("caught exit... shutting down")
      instruction = global_data.instruction_class()
      instruction.group = "system_tasks"
      instruction.task = "shutdown_delay"
      global_data.main_queue.put(instruction, block=False)
      main_thread.stop_thread()

def stop_threads():
   network_thread.stop_thread()

def security_shutdown():
   stop_threads()
   print("done")

print("Setting Up Interrupt Handler")
try:
   signal.signal(signal.SIGINT, exit_handler)
except:
   print("Couldn't lock SIGINT")
try:
   signal.signal(signal.SIGBREAK, exit_handler)
except:
   print("Couldn't lock SIGBREAK")
try:
   signal.signal(signal.SIGKILL, exit_handler)
except:
   print("Couldn't lock SIGKILL")
try:
   signal.signal(signal.SIGQUIT, exit_handler)
except:
   print("Couldn't lock SIGQUIT")
main_thread.start(security_main)
while(main_thread.is_active()):
   main_thread.pause(2)
