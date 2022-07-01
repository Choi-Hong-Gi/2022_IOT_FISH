#include <ESP8266WiFi.h>
#include<Servo.h>
#define ServoPin 12                     //Servo
Servo servo;

const char* ssid = "RPI";
const char* password = "IOT2022*";

int relay = 13; //GPIO
WiFiServer server(80);
IPAddress serverIP={192,168,0,4};      // 접속 IP 설정

WiFiClient client;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(10);

  //LED 세팅
  pinMode(relay, OUTPUT);
  digitalWrite(relay, LOW);

  //서보 모터 
  servo.attach(ServoPin,600,2400);
  servo.write(0);

  //WiFi 연결
  WiFi.disconnect(true);
  delay(1000);
  Serial.print("Connecting to ");
  Serial.print(ssid);

  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(200);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP Address: ");
  Serial.println(WiFi.localIP());

  //Server 시작
  server.begin();
  Serial.println("Server started");
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.print("/");

}

void loop() {
  
  //client 접속 확인
  WiFiClient client = server.available();
    if(!client){
    return;
  }
  //client가 보내는 데이터를 기다린다.
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }

  //요청을 읽는다.
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();
  
  //요청에 url에 따라 LED를 ON/Off
  if (request.indexOf("/ledOn") > 0){
    digitalWrite(relay, HIGH);
    client.print("led on");
  }
  if (request.indexOf("/ledOff") > 0){
    digitalWrite(relay, LOW);
    client.print("led off");
  }
  if (request.indexOf("/Feed") > 0){
    Feed();
    client.print("Feeded.");
  }
  
  
  delay(1);


}
void Feed(){
  servo.write(0);
  delay(1000);
  servo.write(180);
  delay(1000);
  servo.write(0);
}
