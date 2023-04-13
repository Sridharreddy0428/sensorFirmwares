#Ref taken from https://github.com/jiteshsaini/mqtt-demo
# This script will listen data from ESP32 and store in sqlite3 db
import time
import logging,sys
from logging.handlers import RotatingFileHandler
import paho.mqtt.client as mqtt
import sqlite3

# Data logging using logger lib
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
log_formatter = logging.Formatter("%(asctime)s %(message)s")
handler = RotatingFileHandler("edgesub.log", mode="a+", maxBytes=10*1024*1024, backupCount=1, encoding=None, delay=0)
handler.setFormatter(log_formatter)
logger.addHandler(stdout_handler)
logger.addHandler(handler)

def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   client_subscriptions(client)
   logger.info("Connected to MQTT server")

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   logger.info("Disconnected from MQTT server")
   
# a callback functions 
def callback_esp32_sensor1(client, userdata, msg):
    logger.info('ESP sensor1 data: {}'.format(msg.payload.decode('utf-8')))
    dataToDB(msg.payload.decode('utf-8'),"IoT Lab")

def callback_esp32_sensor2(client, userdata, msg):
    logger.info('ESP sensor2 data: {}'.format(msg.payload.decode('utf-8')))
    dataToDB(msg.payload.decode('utf-8'),"Open Hall")

def callback_rpi_broadcast(client, userdata, msg):
    logger.info('RPi Broadcast message:  {}'.format(msg.payload.decode('utf-8')))

def client_subscriptions(client):
    client.subscribe("esp32/#")
    client.subscribe("rpi/broadcast")
    
def mqttClient():
    client = mqtt.Client("rpi_client1") #this should be a unique name
    flag_connected = 0

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.message_callback_add('esp32/sensor1', callback_esp32_sensor1)
    client.message_callback_add('esp32/sensor2', callback_esp32_sensor2)
    client.message_callback_add('rpi/broadcast', callback_rpi_broadcast)
    client.connect('127.0.0.1',1883,60)
    # start a new thread
    client.loop_start()
    client_subscriptions(client)
    logger.info("......client setup complete............")

conn = sqlite3.connect('edgeconnect.db', check_same_thread=False)
c = conn.cursor()

def data_to_table(timestamp,n,v,u,Location):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS esp_data_to_db (timestamp, n, v, u, Location);")
    conn.execute("INSERT INTO esp_data_to_db (timestamp, n, v, u, Location) VALUES (?, ?, ?, ?, ?);",
                 (int(timestamp),str(n), float(v), str(u), str(Location)))

    pastTimeStamp=timestamp-86400
    conn.execute('DELETE FROM esp_data_to_db WHERE timestamp < ?;',[pastTimeStamp])
    conn.commit()

def so2SensorData(data,Location):
    timestamp=int(time.time())
    data_to_table(timestamp,'so2',data[1],'ppb',Location)
    data_to_table(timestamp,'Temperature', data[2],'℃',Location)
    data_to_table(timestamp,'Humidity',data[3],'%RH',Location)

def zphsSensorData(data,Location): 
    timestamp=int(time.time())   
    res=data.split()
#    print("res is ",res)
    if res[0]=='FF' and res[1]=='86':
        pm1=(int(res[2],16))*256+(int(res[3],16))
        data_to_table(timestamp,'pm1.0',pm1,'μg/m³',Location)
    
        pm2=(int(res[4],16))*256+(int(res[5],16))
        data_to_table(timestamp,'pm2.5',pm2,'μg/m³',Location)
    
        pm10=(int(res[6],16))*256+(int(res[7],16))
        data_to_table(timestamp,'pm10',pm10,'μg/m³',Location)
    
        Co2=(int(res[8],16))*256+(int(res[9],16))
        data_to_table(timestamp,'Co2',Co2,'ppm',Location)
    
        VOC=round(int(res[10]),2)
        data_to_table(timestamp,'VOC',pm10,'voc',Location)
    
        #Temp=round((((int(res[11],16))*256+(int(res[12],16)))-500)*0.1,2)
        #data_to_table(timestamp,'Temperature',Temp,'℃',Location)
    
        #Humidity=(int(res[13],16))*256+(int(res[14],16))
        #data_to_table(timestamp,'Humidity',Humidity,' %RH',Location)
    
        CH2O=round(((int(res[15],16))*256 +(int(res[16],16)))*0.001,2)
        data_to_table(timestamp,'CH2O',CH2O,'mg/m³',Location)
    
        CO=round(((int(res[17],16))*256+(int(res[18],16)))*0.1,2)
        data_to_table(timestamp,'CO',CO,'ppm',Location)
    
        O3=round(((int(res[19],16))*256+(int(res[20],16)))*0.01,2)
        data_to_table(timestamp,'O3',O3,'ppm',Location)
    
        No2=round(((int(res[21],16))*256+(int(res[22],16)))*0.01,2)
        data_to_table(timestamp,'No2',No2,'ppm',Location)

def dataToDB(data,Location):
    if data[0]=="|":
        zphs=data.replace('|'," ")[1:]
#        print("updated data located at {} is {}".format(Location,zphs))
        zphsSensorData(zphs,Location)
    else:
        res=data.split(",")
#        print("so2 data is ",res)
#        print("so2 data located at {} is {}".format(Location,so2))
        so2SensorData(res,Location)
if __name__=='__main__':
    mqttClient()
    while True:
        if (flag_connected != 1):
            logger.info("trying to connect MQTT server..")
            mqttClient()
            
        
