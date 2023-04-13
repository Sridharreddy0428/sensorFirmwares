import time
import json
import paho.mqtt.client as mqtt
import serial
import logging
from logging.handlers import RotatingFileHandler
import sys
import re,uuid
import schedule

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

def constructJsonSensor(devicename,devicevalue,deviceunit,properties):
    data = {}
    data["timestamp"]=int(time.time())
    data["n"]=devicename
    data["v"]=devicevalue
    data["u"]=deviceunit
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
NO2_alert=False 
So2_alert=False
def So2Data():
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
    ser.write(b'\r')
    response = ser.readline().decode('ascii').strip()
    so2=int(response.split(',')[1])
    #print(f"SO2 level: {response.split(',')[1]} ppm,Temperature level: {response.split(',')[2]} ℃,Humidity level: {response.split(',')[3]}")
    ser.close()
    return so2  
   
def sensorData():
    global p,pm1_alert,pm2_alert,pm10_alert,Co2_alert,CO_alert,CH2O_alert,VOC_alert,O3_alert,NO2_alert,Temperature_alert,Humidity_alert,So2_alert
    So2=20
    #So2=So2Data()
    childs=[]
    alert_childs=[]
    # Open serial port at 9600 baud rate
    ser = serial.Serial('/dev/ttyUSB0', 9600)

    # Send command to request data
    ser.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')

    # Read the response from the sensor
    response = ser.read(26)
    print('respones is ',response)
    # Parse the response and extract the data
    # AGSM So2 Sensor data
    if So2>p.So2['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('So2',So2,'ppb',properties))
            if not So2_alert:
                So2_alert=True
                alert_childs.append(constructJsonSensor('So2',So2,'ppb',properties))
    elif So2<p.So2['Low']:
        properties=propertiesJson('Need attension','Low')
        childs.append(constructJsonSensor('So2',So2,'ppb',properties))
        if not So2_alert:
            So2_alert=True
            alert_childs.append(constructJsonSensor('So2',So2,'ppb',properties))
    else:
        properties=propertiesJson('Good','Normal')
        So2_alert=False
        childs.append(constructJsonSensor('So2',So2,'ppb',properties))
    #All in One sensor data (ZPHS 01B sensor data)
    if response[0] == 0xff and response[1] == 0x86:
        pm1 = (response[2] * 256 + response[3])
        if pm1>p.pm1['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('pm1.0',pm1,'μg/m³',properties))
            if not pm1_alert:
                pm1_alert=True
                alert_childs.append(constructJsonSensor('pm1.0',pm1,'μg/m³',properties))
        elif pm1<p.pm1['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('pm1.0',pm1,'μg/m³',properties))
            if not pm1_alert:
                pm1_alert=True
                alert_childs.append(constructJsonSensor('pm1.0',pm1,'μg/m³',properties))
        else:
            properties=propertiesJson('Good','Normal')
            pm1_alert=False
            childs.append(constructJsonSensor('pm1.0',pm1,'μg/m³',properties))
            
        pm25 = (response[4] * 256 + response[5])
        if pm25>p.pm25['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('pm2.5',pm25,'μg/m³',properties))
            if not pm2_alert:
                pm2_alert=True
                alert_childs.append(constructJsonSensor('pm2.5',pm25,'μg/m³',properties))
        elif pm25<p.pm25['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('pm2.5',pm25,'μg/m³',properties))
            if not pm2_alert:
                pm2_alert=True
                alert_childs.append(constructJsonSensor('pm2.5',pm25,'μg/m³',properties))
        else:
            properties=propertiesJson('Good','Normal')
            pm2_alert=False
            childs.append(constructJsonSensor('pm2.5',pm25,'μg/m³',properties))
        
        pm10 = (response[6] * 256 + response[7])
        if pm10>p.pm10['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('pm10',pm10,'μg/m³',properties))
            if not pm10_alert:
                pm10_alert=True
                alert_childs.append(constructJsonSensor('pm10',pm10,'μg/m³',properties))
        elif pm10<p.pm10['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('pm10',pm10,'μg/m³',properties))
            if not pm10_alert:
                pm10_alert=True
                alert_childs.append(constructJsonSensor('pm10',pm10,'μg/m³',properties))
        else:
            properties=propertiesJson('Good','Normal')
            pm10_alert=False
            childs.append(constructJsonSensor('pm10',pm10,'μg/m³',properties))
        
        Co2= (response[8] * 256 + response[9])
        if Co2>p.Co2['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('Co2',Co2,'ppm',properties))
            if not Co2_alert:
                Co2_alert=True
                alert_childs.append(constructJsonSensor('Co2',Co2,'ppm',properties))
        elif Co2<p.Co2['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('Co2',Co2,'ppm',properties))
            if not Co2_alert:
                Co2_alert=True
                alert_childs.append(constructJsonSensor('Co2',Co2,'ppm',properties))
        else:
            properties=propertiesJson('Good','Normal')
            Co2_alert=False
            childs.append(constructJsonSensor('Co2',Co2,'ppm',properties))
        
        VOC= response[10]
        if VOC>p.VOC['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('VOC',VOC,'voc',properties))
            if not VOC_alert:
                VOC_alert=True
                alert_childs.append(constructJsonSensor('VOC',VOC,'voc',properties))
        elif VOC<p.VOC['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('VOC',VOC,'voc',properties))
            if not VOC_alert:
                VOC_alert=True
                alert_childs.append(constructJsonSensor('VOC',VOC,'voc',properties))
        else:
            properties=propertiesJson('Good','Normal')
            VOC_alert=False
            childs.append(constructJsonSensor('VOC',VOC,'voc',properties))
            
        Temperature = round(((response[11] * 256 + response[12])-500)*0.1,2)
        if Temperature>p.Temperature['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('Temperature',Temperature,'℃',properties))
            if not Temperature_alert:
                Temperature_alert=True
                alert_childs.append(constructJsonSensor('Temperature',Temperature,'℃',properties))
        elif Temperature<p.Temperature['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('Temperature',Temperature,'℃',properties))
            if not Temperature_alert:
                Temperature_alert=True
                alert_childs.append(constructJsonSensor('Temperature',Temperature,'℃',properties))
        else:
            properties=propertiesJson('Good','Normal')
            Temperature_alert=False
            childs.append(constructJsonSensor('Temperature',Temperature,'℃',properties))
            
        Humidity = (response[13] * 256 + response[14])
        if Humidity>p.Humidity['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('Humidity',Humidity,' %RH',properties))
            if not Humidity_alert:
                Humidity_alert=True
                alert_childs.append(constructJsonSensor('Humidity',Humidity,' %RH',properties))
        elif Humidity<p.Humidity['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('Humidity',Humidity,' %RH',properties))
            if not Humidity_alert:
                Humidity_alert=True
                alert_childs.append(constructJsonSensor('Humidity',Humidity,' %RH',properties))          
        else:
            properties=propertiesJson('Good','Normal')
            Humidity_alert=False
            childs.append(constructJsonSensor('Humidity',Humidity,' %RH',properties))
            
        CH2O= (response[15] * 256 + response[16])*0.001
        if CH2O>p.CH2O['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('CH2O',CH2O,'mg/m³',properties))
            if not CH2O_alert:
                CH2O_alert=True
                alert_childs.append(constructJsonSensor('CH2O',CH2O,'mg/m³',properties))
        elif CH2O<p.CH2O['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('CH2O',CH2O,'mg/m³',properties))
            if not CH2O_alert:
                CH2O_alert=True
                alert_childs.append(constructJsonSensor('CH2O',CH2O,'mg/m³',properties))
        else:
            properties=propertiesJson('Good','Normal')
            CH2O_alert=False
            childs.append(constructJsonSensor('CH2O',CH2O,'mg/m³',properties))
            
        CO= (response[17] * 256 + response[18])*0.1
        if CO>p.CO['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('CO',CO,'ppm',properties))
            if not CO_alert:
                CO_alert=True
                alert_childs.append(constructJsonSensor('CO',CO,'ppm',properties))
        elif CO<p.CO['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('CO',CO,'ppm',properties))
            if not CO_alert:
                CO_alert=True
                alert_childs.append(constructJsonSensor('CO',CO,'ppm',properties))
        else:
            properties=propertiesJson('Good','Normal')
            CO_alert=False
            childs.append(constructJsonSensor('CO',CO,'ppm',properties))
            
        O3= (response[19] * 256 + response[20])*0.01
        if O3>p.O3['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('O3',O3,'ppm',properties))
            if not O3_alert:
                O3_alert=True
                alert_childs.append(constructJsonSensor('O3',O3,'ppm',properties))
        elif O3<p.O3['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('O3',O3,'ppm',properties))
            if not O3_alert:
                O3_alert=True
                alert_childs.append(constructJsonSensor('O3',O3,'ppm',properties))
        else:
            properties=propertiesJson('Good','Normal')
            O3_alert=False
            childs.append(constructJsonSensor('O3',O3,'ppm',properties))
            
        NO2=(response[21] * 256 + response[22])*0.01
        if NO2>p.No2['High']:
            properties=propertiesJson('Need attension','High')
            childs.append(constructJsonSensor('NO2',NO2,'ppm',properties))
            if not NO2_alert:
                NO2_alert=True
                alert_childs.append(constructJsonSensor('NO2',NO2,'ppm',properties))
        elif NO2<p.No2['Low']:
            properties=propertiesJson('Need attension','Low')
            childs.append(constructJsonSensor('NO2',NO2,'ppm',properties))
            if not NO2_alert:
                NO2_alert=True
                alert_childs.append(constructJsonSensor('NO2',NO2,'ppm',properties))    
        else:
            properties=propertiesJson('Good','Normal')
            NO2_alert=False
            childs.append(constructJsonSensor('NO2',NO2,'ppm',properties))
        
        #print(f"PM1.0: {pm1} μg/m³, PM2.5: {pm25} μg/m³,PM10: {pm10} μg/m³,Co2: {Co2} ppm,VOC: {VOC} voc,Temperature: {Temperature} ℃,Humidity: {Humidity} %RH,CH2O: {CH2O} mg/m3,CO :{CO} ppm,O3: {O3} ppm,NO2: {NO2} ppm")
        return  childs,alert_childs
    else:
        print("Invalid response")

    # Close the serial port
    ser.close()

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
    client = mqtt.Client("rpi_client2") #this name should be unique
    client.on_connect=on_connect
    client.on_disconnect=on_disconnect
    client.on_publish = on_publish
    client.connect('127.0.0.1',1883)
    # start a new thread
    client.loop_start()
    return client
      
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
            if pm1_alert or pm2_alert or pm10_alert or VOC_alert or Co2_alert or Temperature_alert or Humidity_alert or CH2O_alert or CO_alert or O3_alert or NO2_alert or So2_alert ==True:
                alert_data=json.dumps(alert_dataToMqtt('IoTLab'))
                if len(alert_data['AirQualityData'])!=0:
                    print("Alert data  payload is {}".format(alert_data))
                    #pubMsg = client.publish(topic='rpi/broadcast',payload=msg.encode('utf-8'),qos=0,)
                    #pubMsg.wait_for_publish()
                    #print(pubMsg.is_published())
                alert_time=int(time.time())
            else:
                logger.info('No Alerts')
                alert_time=int(time.time())
