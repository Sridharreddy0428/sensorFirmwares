import time
import json
#import paho.mqtt.client as mqtt
import serial
import logging
from logging.handlers import RotatingFileHandler
import sys
import re,uuid
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

deviceMacId = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
deviceId=deviceMacId.replace(':','')

def on_publish(client, userdata, mid):
    print("message published with status code ",mid)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT server with status code"+str(rc))

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT server with status code"+str(rc))

def constructJsonSensor(timestamp,devicename,devicevalue,deviceunit,Location,properties):
    data = {}
    data["timestamp"]=timestamp
    data["n"]=devicename
    data["v"]=devicevalue
    data["u"]=deviceunit
    data["Location"]=Location
    data["properties"]=properties
    return data

def propertiesJson(alertStatus,assetstatus):
    properties={}
    properties['alertState']=alertStatus
    properties['assetState']=assetstatus
    return properties

p = lambda:None
sensorConfig_json = r'./resources/sensorConfig.json'
with open(sensorConfig_json) as f:
    p.__dict__ = json.load(f)
    f.close()

#Initializing alert variables
pm1_alert=False
pm2_alert=False
pm10_alert=False
VOC_alert=False
Co2_alert=False
Temperature_alert=False
Humidity_alert=False
CH2O_alert=False
CO_alert=False
O3_alert=False
No2_alert=False 
So2_alert=False

conn=sqlite3.connect('edgeconnect.db', check_same_thread=False)

def fetchDBData(name):
    cursor = conn.execute("SELECT * FROM esp_data_to_db WHERE n=? ORDER BY timestamp DESC LIMIT 1;",[name])
    row = cursor.fetchone()
    timestamp,n,v,u,Location = row
    currentTime = timestamp
    pastHour = int(currentTime) - 3600
    cursor = conn.execute("SELECT AVG(v) FROM esp_data_to_db WHERE n=? AND (timestamp BETWEEN ? AND ?);",[name,pastHour,currentTime])
    avgValue = cursor.fetchone()
    return timestamp,round(avgValue[0],2),n,v,u,Location
   
def sensorData():
    global p,pm1_alert,pm2_alert,pm10_alert,Co2_alert,CO_alert,CH2O_alert,VOC_alert,O3_alert,No2_alert,Temperature_alert,Humidity_alert,So2_alert

    timestamp,avg_So2,n,So2,u,Location=fetchDBData('so2')
    childs=[]
    alert_childs=[]
    if So2>p.So2['High']:
            properties=propertiesJson('Need attention','High')
            childs.append(constructJsonSensor(timestamp,n,So2,u,Location,properties))
            if not So2_alert:
                So2_alert=True
                alert_childs.append(constructJsonSensor(timestamp,n,So2,u,Location,properties))
    elif So2<p.So2['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,So2,u,Location,properties))
        if not So2_alert:
            So2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,So2,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        So2_alert=False
        childs.append(constructJsonSensor(timestamp,n,So2,u,Location,properties))
    #All in One sensor data (ZPHS 01B sensor data)
    timestamp,avg_pm1,n,pm1,u,Location=fetchDBData('pm1.0')
    if pm1>p.pm1['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,pm1,u,Location,properties))
        if not pm1_alert:
            pm1_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm1,u,Location,properties))
    elif pm1<p.pm1['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,pm1,u,Location,properties))
        if not pm1_alert:
            pm1_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm1,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        pm1_alert=False
        childs.append(constructJsonSensor(timestamp,n,pm1,u,Location,properties))
        
    timestamp,avg_pm25,n,pm25,u,Location=fetchDBData('pm2.5')
    if pm25>p.pm25['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,pm25,u,Location,properties))
        if not pm2_alert:
            pm2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm25,u,Location,properties))
    elif pm25<p.pm25['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,pm25,u,Location,properties))
        if not pm2_alert:
            pm2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm25,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        pm2_alert=False
        childs.append(constructJsonSensor(timestamp,n,pm25,u,Location,properties))
    
    timestamp,avg_pm10,n,pm10,u,Location=fetchDBData('pm10')
    if pm10>p.pm10['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,pm10,u,Location,properties))
        if not pm10_alert:
            pm10_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm10,u,Location,properties))
    elif pm10<p.pm10['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,pm10,u,Location,properties))
        if not pm10_alert:
            pm10_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,pm10,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        pm10_alert=False
        childs.append(constructJsonSensor(timestamp,n,pm10,u,Location,properties))
    
    timestamp,avg_Co2,n,Co2,u,Location=fetchDBData('Co2')
    if Co2>p.Co2['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,Co2,u,Location,properties))
        if not Co2_alert:
            Co2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Co2,u,Location,properties))
    elif Co2<p.Co2['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,Co2,u,Location,properties))
        if not Co2_alert:
            Co2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Co2,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        Co2_alert=False
        childs.append(constructJsonSensor(timestamp,n,Co2,u,Location,properties))
    
    timestamp,avg_VOC,n,VOC,u,Location=fetchDBData('VOC')
    if VOC>p.VOC['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,VOC,u,Location,properties))
        if not VOC_alert:
            VOC_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,VOC,u,Location,properties))
    elif VOC<p.VOC['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,VOC,u,Location,properties))
        if not VOC_alert:
            VOC_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,VOC,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        VOC_alert=False
        childs.append(constructJsonSensor(timestamp,n,VOC,u,Location,properties))
        
    timestamp,avg_Temperature,n,Temperature,u,Location=fetchDBData('Temperature')
    if Temperature>p.Temperature['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,Temperature,u,Location,properties))
        if not Temperature_alert:
            Temperature_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Temperature,u,Location,properties))
    elif Temperature<p.Temperature['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,Temperature,u,Location,properties))
        if not Temperature_alert:
            Temperature_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Temperature,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        Temperature_alert=False
        childs.append(constructJsonSensor(timestamp,n,Temperature,u,Location,properties))
        
    timestamp,avg_Humidity,n,Humidity,u,Location=fetchDBData('Humidity')
    if Humidity>p.Humidity['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,Humidity,u,Location,properties))
        if not Humidity_alert:
            Humidity_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Humidity,u,Location,properties))
    elif Humidity<p.Humidity['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,Humidity,u,Location,properties))
        if not Humidity_alert:
            Humidity_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,Humidity,u,Location,properties))          
    else:
        properties=propertiesJson('Good','Normal')
        Humidity_alert=False
        childs.append(constructJsonSensor(timestamp,n,Humidity,u,Location,properties))
        
    timestamp,avg_CH2O,n,CH2O,u,Location=fetchDBData('CH2O')
    if CH2O>p.CH2O['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,CH2O,u,Location,properties))
        if not CH2O_alert:
            CH2O_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,CH2O,u,Location,properties))
    elif CH2O<p.CH2O['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,CH2O,u,Location,properties))
        if not CH2O_alert:
            CH2O_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,CH2O,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        CH2O_alert=False
        childs.append(constructJsonSensor(timestamp,n,CH2O,u,Location,properties))
        
    timestamp,avg_CO,n,CO,u,Location=fetchDBData('CO')
    if CO>p.CO['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,CO,u,Location,properties))
        if not CO_alert:
            CO_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,CO,u,Location,properties))
    elif CO<p.CO['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,CO,u,Location,properties))
        if not CO_alert:
            CO_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,CO,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        CO_alert=False
        childs.append(constructJsonSensor(timestamp,n,CO,u,Location,properties))
        
    timestamp,avg_O3,n,O3,u,Location=fetchDBData('O3')
    if O3>p.O3['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,O3,u,Location,properties))
        if not O3_alert:
            O3_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,O3,u,Location,properties))
    elif O3<p.O3['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,O3,u,Location,properties))
        if not O3_alert:
            O3_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,O3,u,Location,properties))
    else:
        properties=propertiesJson('Good','Normal')
        O3_alert=False
        childs.append(constructJsonSensor(timestamp,n,O3,u,Location,properties))
        
    timestamp,avg_No2,n,No2,u,Location=fetchDBData('No2')
    if No2>p.No2['High']:
        properties=propertiesJson('Need attention','High')
        childs.append(constructJsonSensor(timestamp,n,No2,u,Location,properties))
        if not No2_alert:
            No2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,No2,u,Location,properties))
    elif No2<p.No2['Low']:
        properties=propertiesJson('Need attention','Low')
        childs.append(constructJsonSensor(timestamp,n,No2,u,Location,properties))
        if not No2_alert:
            No2_alert=True
            alert_childs.append(constructJsonSensor(timestamp,n,No2,u,Location,properties))    
    else:
        properties=propertiesJson('Good','Normal')
        No2_alert=False
        childs.append(constructJsonSensor(timestamp,n,No2,u,Location,properties))
    
    logger.info(f"PM1.0: {avg_pm1} μg/m³, PM2.5: {avg_pm25} μg/m³,PM10: {avg_pm10} μg/m³,Co2: {avg_Co2} ppm,VOC: {avg_VOC} voc,Temperature: {avg_Temperature} ℃,Humidity: {avg_Humidity} %RH,CH2O: {avg_CH2O} mg/m3,CO :{avg_CO} ppm,O3: {avg_O3} ppm,NO2: {avg_No2} ppm")
    
    return  childs,alert_childs

def dataToMqtt(Location):
    global deviceId
    childs,alertChilds=sensorData()
    data={}
    data['_id']=deviceId
    data['location']=Location
    data['AirQualityData']=childs
    return data 

def alert_dataToMqtt(Location):
    global deviceId
    childs,alert_Childs=sensorData()
    data={}
    data['_id']=deviceId
    data['location']=Location
    data['AirQualityData']=alert_Childs
    return data 
  
def mqttConnection():
    client1 = mqtt.Client("rpi_client20") #this name should be unique
    client1.on_connect=on_connect
    client1.on_disconnect=on_disconnect
    client1.on_publish = on_publish
    client1.connect('127.0.0.1',1883)
    # start a new thread
    client1.loop_start()
    return client1
      
if __name__=='__main__':
    #client=mqttConnection()
    start_time=int(time.time())
    alert_time=int(time.time())
    while True:
        if int(time.time())-start_time>=300:
            msg=json.dumps(dataToMqtt('IoT Lab'))
            logger.info("Regular data is {}".format(msg))
            #pubMsg = client.publish(topic='rpi/broadcast',payload=msg.encode('utf-8'),qos=0,)
            #pubMsg.wait_for_publish()
            #print(pubMsg.is_published())
            start_time=int(time.time())
        if int(time.time())-alert_time>=60:
            alert_data=alert_dataToMqtt('IoTLab')
            if pm1_alert or pm2_alert or pm10_alert or VOC_alert or Co2_alert or Temperature_alert or Humidity_alert or CH2O_alert or CO_alert or O3_alert or No2_alert or So2_alert ==True:
                if alert_data['AirQualityData']:
                    alert_data=json.dumps(alert_data)
                    logger.info("Alert data  payload is {}".format(alert_data))
                    #pubMsg = client.publish(topic='rpi/broadcast',payload=msg.encode('utf-8'),qos=0,)
                    #pubMsg.wait_for_publish()
                    #print(pubMsg.is_published())
                else:
                    logger.info('No Alerts')
                alert_time=int(time.time())
            else:
                logger.info('No Alerts')
                alert_time=int(time.time())
