


#function to go through sensors in database and create threads for all of them, passing config option and pin etc

#function to kill and join all threads so we can reload and restart the sensors

#thread function to send events back to main queue for processing

import security_threads
import global_data
import database
import queue
import gpio

class sensor_class:
   def __init__(self, name="sensor", location = 0, event_type = 0, db_id = 0, ms_period = 1000):
      self.name = name
      self.location = location
      self.event_type = event_type
      self.ms_period = ms_period
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
   if("ms_period" in instruction):
      new_sensor.ms_period = instruction["ms_period"]
   new_sensor_dict = vars(new_sensor)
   new_sensor_dict.pop("db_id")
   database.add_db_sensor(new_sensor_dict)

def remove_sensor(instruction):
   database.remove_db_sensor(instruction["db_id"])

def sensor_process(sensor_thread, args):
   sensor = args[0]

   sensor_instruction = global_data.instruction_class()
   sensor_instruction.group = "sensor_task"
   sensor_instruction.task = "sensor_triggered"
   sensor_instruction.data = 0
   
   print("Sensor Process Started")

   if(sensor.event_type == 0): # polled sensor - active low
      gpio.set_gpio_mode_polled_input(sensor.location)
   if(sensor.event_type == 1): # polled sensor - active high
      gpio.set_gpio_mode_polled_input(sensor.location)
   if(sensor.event_type == 2): # interrupt sensor - falling low
      gpio.set_gpio_mode_interrupt_low_input(sensor.location)
   if(sensor.event_type == 3): # interrupt sensor - rising high
      gpio.set_gpio_mode_interrupt_high_input(sensor.location)
   
   while (sensor_thread.is_active()):
      sensor_triggered = 0
      while(not sensor.thread_queue.empty()):
         try:
            new_queue_data = sensor.thread_queue.get(block=False)
         except:
            #network queue was empty and timed out
            pass
         else:
            print("got sensor data")
      
      if(sensor.event_type == 0): # polled sensor - active low
         gpio_level = gpio.get_gpio_level()
         if(gpio_level == 0):
            sensor_triggered = 1
         sensor_thread.pause(sensor.ms_period/1000)
         
      if(sensor.event_type == 1): # polled sensor - active high
         gpio_level = gpio.get_gpio_level()
         if(gpio_level == 1):
            sensor_triggered = 1
         sensor_thread.pause(sensor.ms_period/1000)

      if(sensor.event_type == 0): # interrupt sensor - falling low
         gpio_level = gpio.wait_gpio_irq_low()
         if(gpio_level == 0):
            sensor_triggered = 1
      if(sensor.event_type == 0): # interrupt sensor - rising high
         gpio_level = gpio.wait_gpio_irq_high()
         if(gpio_level == 1):
            sensor_triggered = 1

      if(sensor_triggered):
         global_data.main_queue.put(sensor_instruction)
