/*
 * KisanMitra Smart Irrigation System - NodeMCU WiFi Version
 * Enhanced with Farmer Notification & 6-Second Response Window
 * 
 * WIRING:
 * - Soil Sensor AO → A0
 * - Green LED → D2 (with 220Ω resistor)
 * - Red LED → D3 (with 220Ω resistor)
 * - Buzzer → D6
 * - Relay IN → D7
 * - LCD SDA → D1
 * - LCD SCL → D5
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ==================== WIFI CONFIGURATION ====================
const char* ssid = "GITAM";
const char* password = "Gitam$$123";
const char* backendUrl = "http://172.20.129.86:5000/api/irrigation";
// ============================================================

#define SOIL_PIN A0
#define RELAY_PIN D7
#define GREEN_LED D2
#define RED_LED D3
#define BUZZER D6

int threshold = 40;
const int COUNTDOWN_SECONDS = 15;
const int BLINK_INTERVAL = 1000;
const unsigned long COOLDOWN_MS = 30000;  // 30 second cooldown after pump cycle

bool motorOn = false;
bool alertActive = false;
bool waitingForFarmer = false;
int countdownRemaining = 0;
unsigned long alertStartTime = 0;
unsigned long lastBlinkTime = 0;
bool ledBlinkState = false;
String currentStatus = "STARTING";
String activatedBy = "";
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000;
unsigned long lastPumpOffTime = 0;  // Track when pump was last turned off

LiquidCrystal_I2C lcd(0x27, 16, 2);
ESP8266WebServer server(80);
int currentMoisture = 0;

void handleRoot() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<meta http-equiv='refresh' content='2'>";
  html += "<title>KisanMitra Irrigation</title>";
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#1a5f2a,#2d8f47);min-height:100vh;margin:0;padding:20px;color:white;}";
  html += ".card{background:rgba(255,255,255,0.95);border-radius:16px;padding:24px;margin:16px auto;max-width:400px;color:#333;box-shadow:0 8px 32px rgba(0,0,0,0.2);}";
  html += "h1{text-align:center;margin-bottom:8px;}";
  html += ".subtitle{text-align:center;opacity:0.9;margin-bottom:24px;}";
  html += ".value{font-size:48px;font-weight:bold;text-align:center;}";
  html += ".label{font-size:14px;color:#666;text-align:center;margin-top:8px;}";
  html += ".status{padding:12px 24px;border-radius:8px;text-align:center;font-weight:bold;margin:16px 0;}";
  html += ".dry{background:#FFEBEE;color:#C62828;}";
  html += ".wet{background:#E8F5E9;color:#2E7D32;}";
  html += ".alert{background:#FFF3E0;color:#E65100;animation:pulse 1s infinite;}";
  html += ".motor-on{background:#E3F2FD;color:#1565C0;}";
  html += ".motor-off{background:#F5F5F5;color:#616161;}";
  html += ".btn{display:block;width:100%;padding:16px;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin-top:16px;}";
  html += ".btn-on{background:#4CAF50;color:white;}";
  html += ".btn-off{background:#f44336;color:white;}";
  html += ".btn-urgent{background:#FF5722;color:white;animation:pulse 0.5s infinite;}";
  html += ".countdown{font-size:32px;text-align:center;color:#E65100;font-weight:bold;}";
  html += ".info{font-size:12px;color:#666;text-align:center;margin-top:16px;}";
  html += "@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.7;}}";
  html += "</style></head><body>";
  
  html += "<h1>🌱 KisanMitra</h1>";
  html += "<p class='subtitle'>Smart Irrigation System</p>";
  html += "<div class='card'>";
  html += "<div class='label'>SOIL MOISTURE</div>";
  html += "<div class='value'>" + String(currentMoisture) + "%</div>";
  
  if (alertActive && waitingForFarmer) {
    html += "<div class='status alert'>🚨 LOW MOISTURE ALERT!</div>";
    html += "<div class='countdown'>⏱️ Auto-start in: " + String(countdownRemaining) + "s</div>";
    html += "<a href='/motor/on'><button class='btn btn-urgent'>💧 TURN ON PUMP NOW!</button></a>";
  } else if (currentMoisture < threshold) {
    html += "<div class='status dry'>⚠️ SOIL DRY - Needs Water</div>";
  } else {
    html += "<div class='status wet'>✅ SOIL OPTIMAL</div>";
  }
  
  if (motorOn) {
    html += "<div class='status motor-on'>🔄 PUMP RUNNING";
    if (activatedBy.length() > 0) {
      html += " (" + activatedBy + ")";
    }
    html += "</div>";
  } else {
    html += "<div class='status motor-off'>⏸️ PUMP OFF</div>";
  }
  
  if (!motorOn) {
    html += "<a href='/motor/on'><button class='btn btn-on'>💧 Turn Pump ON</button></a>";
  } else {
    html += "<a href='/motor/off'><button class='btn btn-off'>🛑 Turn Pump OFF</button></a>";
  }
  
  html += "<p class='info'>Threshold: " + String(threshold) + "% | Status: " + currentStatus + "</p>";
  html += "<p class='info'>IP: " + WiFi.localIP().toString() + "</p>";
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

void handleApi() {
  String json = "{";
  json += "\"moisture\":" + String(currentMoisture) + ",";
  json += "\"motorStatus\":" + String(motorOn ? "true" : "false") + ",";
  json += "\"status\":\"" + currentStatus + "\",";
  json += "\"threshold\":" + String(threshold) + ",";
  json += "\"alertActive\":" + String(alertActive ? "true" : "false") + ",";
  json += "\"waitingForFarmer\":" + String(waitingForFarmer ? "true" : "false") + ",";
  json += "\"countdownRemaining\":" + String(countdownRemaining) + ",";
  json += "\"activatedBy\":\"" + activatedBy + "\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"uptime\":" + String(millis() / 1000);
  json += "}";
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void handleMotorOn() {
  digitalWrite(RELAY_PIN, LOW);
  motorOn = true;
  
  if (alertActive && waitingForFarmer) {
    activatedBy = "FARMER";
    currentStatus = "FARMER_ACTIVATED";
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Web Control!");
    lcd.setCursor(0, 1);
    lcd.print("Motor: ON");
  } else {
    activatedBy = "MANUAL";
    currentStatus = "MANUAL_ON";
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WEB CONTROL");
    lcd.setCursor(0, 1);
    lcd.print("Motor: ON");
  }
  
  alertActive = false;
  waitingForFarmer = false;
  countdownRemaining = 0;
  
  digitalWrite(RED_LED, HIGH);
  digitalWrite(BUZZER, LOW);
  digitalWrite(GREEN_LED, LOW);
  
  // CORS headers for browser access
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.send(200, "application/json", "{\"success\":true,\"motor\":true,\"status\":\"" + currentStatus + "\"}");
}

void handleMotorOff() {
  digitalWrite(RELAY_PIN, HIGH);
  motorOn = false;
  activatedBy = "";
  currentStatus = "MANUAL_OFF";
  lastPumpOffTime = millis();  // Start cooldown timer
  
  digitalWrite(RED_LED, LOW);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WEB CONTROL");
  lcd.setCursor(0, 1);
  lcd.print("Motor: OFF");
  
  // CORS headers for browser access
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.send(200, "application/json", "{\"success\":true,\"motor\":false,\"status\":\"" + currentStatus + "\"}");
}

void sendToBackend() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  WiFiClient client;
  HTTPClient http;
  
  http.begin(client, backendUrl);
  http.addHeader("Content-Type", "application/json");
  
  String json = "{";
  json += "\"moisture\":" + String(currentMoisture) + ",";
  json += "\"motor\":" + String(motorOn ? "true" : "false") + ",";
  json += "\"status\":\"" + currentStatus + "\",";
  json += "\"alertActive\":" + String(alertActive ? "true" : "false") + ",";
  json += "\"countdownRemaining\":" + String(countdownRemaining) + ",";
  json += "\"activatedBy\":\"" + activatedBy + "\",";
  json += "\"farmerId\":\"nodemcu-wifi\"";
  json += "}";
  
  http.POST(json);
  http.end();
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=== KisanMitra Smart Irrigation ===");
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(BUZZER, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);

  Wire.begin(D1, D5);
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("  Welcome to   ");
  lcd.setCursor(0, 1);
  lcd.print(" Kisaan Mitra! ");
  delay(2000);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart Irrigation");
  lcd.setCursor(0, 1);
  lcd.print("WiFi Connecting..");
  
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[OK] WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected!");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP());
    
    for (int i = 0; i < 3; i++) {
      digitalWrite(GREEN_LED, HIGH);
      delay(200);
      digitalWrite(GREEN_LED, LOW);
      delay(200);
    }
  } else {
    Serial.println("\n[ERROR] WiFi Failed!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi FAILED!");
    lcd.setCursor(0, 1);
    lcd.print("Running Offline");
  }
  
  delay(2000);
  
  server.on("/", handleRoot);
  server.on("/api", handleApi);
  server.on("/api/data", handleApi);
  server.on("/motor/on", handleMotorOn);
  server.on("/motor/off", handleMotorOff);
  
  server.begin();
  Serial.println("[OK] HTTP Server started");
  Serial.println("Open: http://" + WiFi.localIP().toString());
  
  lcd.clear();
  currentStatus = "READY";
}

void loop() {
  server.handleClient();
  
  int soilValue = analogRead(SOIL_PIN);
  currentMoisture = map(soilValue, 1023, 0, 0, 100);
  currentMoisture = constrain(currentMoisture, 0, 100);

  // Only trigger alert if: moisture low, motor off, and cooldown elapsed
  bool cooldownElapsed = (millis() - lastPumpOffTime) > COOLDOWN_MS;
  
  if (currentMoisture < threshold && motorOn == false && cooldownElapsed) {
    
    if (!alertActive) {
      alertActive = true;
      waitingForFarmer = true;
      alertStartTime = millis();
      countdownRemaining = COUNTDOWN_SECONDS;
      lastBlinkTime = millis();
      ledBlinkState = false;
      currentStatus = "ALERT_WAITING";
      activatedBy = "";
      
      Serial.println("[ALERT] Low moisture! Waiting for farmer...");
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("! LOW MOISTURE !");
      lcd.setCursor(0, 1);
      lcd.print("Moist: ");
      lcd.print(currentMoisture);
      lcd.print("%");
    }
    
    if (waitingForFarmer) {
      unsigned long elapsed = millis() - alertStartTime;
      countdownRemaining = COUNTDOWN_SECONDS - (elapsed / 1000);
      if (countdownRemaining < 0) countdownRemaining = 0;
      
      if (millis() - lastBlinkTime >= BLINK_INTERVAL) {
        lastBlinkTime = millis();
        ledBlinkState = !ledBlinkState;
        
        digitalWrite(RED_LED, ledBlinkState ? HIGH : LOW);
        digitalWrite(BUZZER, ledBlinkState ? HIGH : LOW);
        digitalWrite(GREEN_LED, LOW);
        
        lcd.setCursor(0, 0);
        lcd.print("Alert! Timer: ");
        lcd.print(countdownRemaining);
        lcd.print("s");
        lcd.setCursor(0, 1);
        lcd.print("Moisture: ");
        lcd.print(currentMoisture);
        lcd.print("%  ");
        
        Serial.print("[COUNTDOWN] ");
        Serial.print(countdownRemaining);
        Serial.println("s remaining...");
      }
      
      if (countdownRemaining <= 0) {
        Serial.println("[AUTO] Auto-starting pump!");
        
        digitalWrite(RELAY_PIN, LOW);
        motorOn = true;
        alertActive = false;
        waitingForFarmer = false;
        activatedBy = "AUTO";
        currentStatus = "AUTO_ACTIVATED";
        
        digitalWrite(RED_LED, HIGH);
        digitalWrite(BUZZER, LOW);
        
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("AUTO-STARTED!");
        lcd.setCursor(0, 1);
        lcd.print("Motor Running...");
      }
    }
  }
  
  else if (motorOn) {
    currentStatus = "MOTOR_RUNNING";
    
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(BUZZER, LOW);
    
    lcd.setCursor(0, 0);
    lcd.print("Motor Running   ");
    lcd.setCursor(0, 1);
    lcd.print("Moisture: ");
    lcd.print(currentMoisture);
    lcd.print("%  ");
    
    if (currentMoisture >= threshold + 10) {
      Serial.println("[AUTO-OFF] Soil wet. Turning off motor.");
      
      digitalWrite(RELAY_PIN, HIGH);
      motorOn = false;
      alertActive = false;
      activatedBy = "";
      currentStatus = "AUTO_OFF";
      lastPumpOffTime = millis();  // Start cooldown timer
      
      digitalWrite(RED_LED, LOW);
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Soil Watered!");
      lcd.setCursor(0, 1);
      lcd.print("Motor: OFF");
      
      delay(2000);
    }
  }

  else if (currentMoisture >= threshold) {
    currentStatus = "WET_OPTIMAL";
    alertActive = false;
    waitingForFarmer = false;
    countdownRemaining = 0;
    
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    digitalWrite(BUZZER, LOW);
    digitalWrite(RELAY_PIN, HIGH);

    lcd.setCursor(0, 0);
    lcd.print("Soil: OPTIMAL   ");
    lcd.setCursor(0, 1);
    lcd.print("Moisture: ");
    lcd.print(currentMoisture);
    lcd.print("%  ");
  }

  if (millis() - lastSendTime > sendInterval) {
    sendToBackend();
    lastSendTime = millis();
    
    Serial.print("Moisture: ");
    Serial.print(currentMoisture);
    Serial.print("% | Motor: ");
    Serial.print(motorOn ? "ON" : "OFF");
    Serial.print(" | Alert: ");
    Serial.print(alertActive ? "YES" : "NO");
    Serial.print(" | Status: ");
    Serial.println(currentStatus);
  }

  delay(100);
}
