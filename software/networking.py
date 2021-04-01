import socket
import global_data
import database
import select
import json

select_timeout = 1
system_config = 0

local_socket_list = []

class my_socket_class:
   socket = 0
   active = 0
   is_get = 0
   ready = 0
   done = 0

def get_my_ip():
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   try:
      # doesn't even have to be reachable
      s.connect(('255.255.255.255', 1))
      ip_address = s.getsockname()[0]
   except Exception:
      try:
         # doesn't even have to be reachable
         s.connect(('10.255.255.255', 1))
         ip_address = s.getsockname()[0]
      except Exception:
         ip_address = '127.0.0.1'
   finally:
      s.close()
   return ip_address

# start network thread
# parent will kill and restart network thread if any config (ip or port) changes
   
def network_listener(network_thread):
   global local_socket_list

   network_thread.pause(1)

   system_config = database.get_db_config()
   system_ip = get_my_ip()
   system_port = system_config.web_port
   max_devices = 5

   print("Starting network thread")

   header_okay = "HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n"
   header_content = "Content-Length: "
   header_end = "Connection: close\r\nContent-Type: text/html\r\nX-Pad: avoid browser bug\r\n\r\n"

   serversocket = 0
   # create an INET, STREAMing socket
   while network_thread.is_active() and serversocket == 0:
      try:
         serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         serversocket.setblocking(False)
         serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         serversocket.bind((system_ip, system_port))
         # become a server socket
         serversocket.listen(max_devices)
      except:
         print("Couldn't connect network listener")
         serversocket = 0
         network_thread.pause(2)

   while (network_thread.is_active()):
      while(not global_data.network_queue.empty()):
         try:
            new_queue_data = global_data.network_queue.get(block=False)
         except:
            #network queue was empty and timed out
            pass
         else:
            for dev in local_socket_list:
               if(new_queue_data.socket == dev.socket):
                  if(dev.is_get):
                     write_data = new_queue_data.data_to_json()
                     packet_data = header_okay+header_content+str(len(write_data))+header_end+write_data
                     write_data_encode = packet_data.encode()
                     dev.socket.send(write_data_encode)
                     dev.done = 1
                     dev.socket.shutdown(socket.SHUT_RDWR)
                     dev.socket.close()

      # Process ready devices
      for dev in local_socket_list:
         if(dev.ready):
            dev.ready = 0
            data = dev.socket.recv(1024)
            instruction = global_data.instruction_class()
            instruction.group = "network_task"
            instruction.task = ""
            instruction.data = data.decode()
            if(instruction.data[0:3] == "GET"):
               offset = instruction.data.find("q={")
               end_offset = instruction.data.find("}")+1
               instruction.data = instruction.data[offset+2:end_offset]
               instruction.data = json.loads(instruction.data)
               instruction.task = "get"
               instruction.socket = dev.socket
               global_data.main_queue.put(instruction)
               dev.active = 0
               dev.is_get = 1
            else:
               if(instruction.data[0:4] == "POST"):
                  offset = instruction.data.find("q={")
                  end_offset = instruction.data.find("}")+1
                  instruction.data = instruction.data[offset+2:end_offset]
                  instruction.data = json.loads(instruction.data)
                  instruction.task = "post"
                  instruction.socket = dev.socket
                  global_data.main_queue.put(instruction)
                  packet_data = header_okay+header_end
                  write_data_encode = packet_data.encode()
                  dev.socket.send(write_data_encode)
                  dev.active = 0
                  dev.done = 1
                  dev.is_get = 0
                  dev.socket.shutdown(socket.SHUT_RDWR)
                  dev.socket.close()
               else:
                  pass
                  # dev.active = 0
                  # dev.done = 1
                  # dev.is_get = 0

      for dev in local_socket_list:
         if(dev.done):
            dev.done = 0
            local_socket_list.remove(dev)
         # if(dev.is_get and dev.done):
         #    dev.done = 0
         #    local_socket_list.remove(dev)
      
      rx_list = [serversocket]
      for local_device in local_socket_list:
         rx_list.append(local_device.socket)

      tx_list = []
      for local_device in local_socket_list:
         if(local_device.is_get):
            tx_list.append(local_device.socket)

      rx_ready, tx_ready, x_ready = select.select(rx_list, tx_list, [], select_timeout)
      
      for ready in rx_ready:
         if(ready == serversocket):
            try:
               new_socket, new_address = serversocket.accept()
               if(new_address[0] == system_ip):
                  new_sock = my_socket_class()
                  new_sock.socket = new_socket
                  new_sock.ready = 1
                  new_sock.active = 1
                  local_socket_list.append(new_sock)
               else:
                  pass
            except:
               print("accept exception")
         else:
            for local_sock in local_socket_list:
               if(ready == local_sock.socket):
                  local_sock.ready = 1

   if(serversocket):
      serversocket.close()
