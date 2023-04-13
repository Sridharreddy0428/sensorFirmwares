#include <WiFi.h>
#include <HardwareSerial.h>
#include <PubSubClient.h>
#include <ESPping.h>

char ssid[] = "Techolution";
char password[] = "wearethebest";
IPAddress remote_ip(192,168,2,9); // IP address of the remote host to ping

HardwareSerial zphsSerial(1); // RX, TX
HardwareSerial so2Serial(2); // RX, TX

unsigned long previousMillis = 0;  // Variable to store the previous time the function was called
const unsigned long interval = 60000;  // Interval (in milliseconds) between function calls
unsigned long currentMillis =0;

const char* mqtt_server = "192.168.2.9";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  // Connect to WiFi network
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  client.setServer(mqtt_server, 1883);
      
  while (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    Serial.println("Connecting to WiFi...");
    }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to WiFi...");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
  }

  // set the data rate for the SoftwareSerial/HardwareSerial port
  so2Serial.begin(9600, SERIAL_8N1, 16, 17); // RX2 ,TX2 initialize the SO2 sensor on UART 2
  zphsSerial.begin(9600, SERIAL_8N1, 26, 27); // RX, TX initialize the ZPHS sensor on UART 1
}

String getSo2Data(){
   so2Serial.write((const uint8_t*)"\r", 1);//writing command to sensor
   String data = so2Serial.readString(); //Reading data from the sensor
//   Serial.println(data);
   return data;
   }
   
String AllinOne(){
    uint8_t command[] = { 0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79 };
    uint8_t data[26];
    char buffer1[26];
    String res = "";
    zphsSerial.write(command,9);
    delay(10);
    if(zphsSerial.available()){
       zphsSerial.readBytes(data, 26); // Read 26 bytes of data from Serial
//      Serial.println("\n data available\n");
       for(int i=0;i<26;i++){
//       Serial.printf("|%X",data[i]);
       sprintf(buffer1,"|%X",data[i]);
       res += buffer1;
      }
      return res;
    }
     else{
      Serial.println("\n data not available\n");
      return " ";
     }
  }

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT broker...");
    if (client.connect("esp32_client_1")) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
} 
void loop() { 
  // Check if WiFi connection is still active
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost. Reconnecting...");
    delay(1000);
    WiFi.begin(ssid, password);
  }
  else{
    Serial.print("Connected to WiFi with Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
    if (Ping.ping(remote_ip)) {
    Serial.println("Ping successful!");
    delay(60000);
    } else {
    Serial.println("Ping failed.");
    delay(5000);
  }  
  }
  if (!client.connected()) {
    Serial.println("client not connected.....");
    reconnect();
    }
  client.loop();
   currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
      Serial.print(" all in one data is : ");
      String zphs = AllinOne();
      Serial.println(zphs);
      if (client.publish("esp32/sensor1", zphs.c_str())){
        Serial.println("zphs data sent to mqtt server ");
      }else {
        Serial.println("Failed to publish zphs message to topic");
        }
      Serial.print(" so2 Data is : ");
      String so2Data = getSo2Data();
      Serial.println(so2Data.c_str());
      if (client.publish("esp32/sensor1", so2Data.c_str())){
        Serial.println("so2 data sent to mqtt server ");
      }else {
        Serial.println("Failed to publish so2 message to topic");
        }
  }  
}
