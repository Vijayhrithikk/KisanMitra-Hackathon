/*
 * KisanMitra Smart Irrigation System
 * With 6-second countdown buzzer and LCD display
 * 
 * FLOW:
 * 1. Check moisture continuously
 * 2. If DRY → Red LED ON, Buzzer countdown 6 seconds
 * 3. LCD shows countdown timer
 * 4. After 6 seconds → Auto turn ON pump
 * 5. When pump ON → Buzzer stops
 * 6. Pump runs until moisture is satisfied
 * 7. If WET → Green LED ON, Pump OFF
 * 
 * CONNECTIONS:
 * - Soil Sensor: AO→A0, VCC→5V, GND→GND
 * - Relay: IN→D7, VCC→5V, GND→GND
 * - Green LED: D4 (with 220Ω)
 * - Red LED: D5 (with 220Ω)
 * - Buzzer: D6
 * - LCD I2C: SDA→A4, SCL→A5, VCC→5V, GND→GND
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SOIL_PIN A0
#define RELAY_PIN 7
#define GREEN_LED 4
#define RED_LED 5
#define BUZZER 6

int threshold = 40;           // Moisture threshold %
bool motorOn = false;
bool countdownActive = false;
int countdownSeconds = 6;
unsigned long pumpStartTime = 0;
String inputCommand = "";

// LCD at address 0x27 (try 0x3F if not working)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
    Serial.begin(9600);
    
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);
    
    digitalWrite(RELAY_PIN, HIGH);  // Motor OFF (active LOW relay)
    digitalWrite(BUZZER, LOW);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, LOW);
    
    // Initialize LCD
    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("  KisanMitra");
    lcd.setCursor(0, 1);
    lcd.print(" Smart Irrigation");
    
    delay(2000);
    lcd.clear();
    
    Serial.println("READY:KisanMitra Smart Irrigation");
}

void loop() {
    // Read soil moisture
    int soilValue = analogRead(SOIL_PIN);
    int moisture = map(soilValue, 1023, 0, 0, 100);
    moisture = constrain(moisture, 0, 100);
    
    // Check serial commands from webpage
    checkSerialCommands();
    
    // ========== MAIN LOGIC ==========
    
    if (moisture < threshold) {
        // SOIL IS DRY
        digitalWrite(RED_LED, HIGH);
        digitalWrite(GREEN_LED, LOW);
        
        if (!motorOn && !countdownActive) {
            // Start 6-second countdown
            countdownActive = true;
            countdownSequence(moisture);
        }
        
        if (motorOn) {
            // Motor is running - show status
            unsigned long runTime = (millis() - pumpStartTime) / 1000;
            displayMotorRunning(moisture, runTime);
        }
        
    } else {
        // SOIL IS WET (moisture >= threshold)
        digitalWrite(GREEN_LED, HIGH);
        digitalWrite(RED_LED, LOW);
        digitalWrite(BUZZER, LOW);
        countdownActive = false;
        
        if (motorOn) {
            // Turn off pump - soil is wet enough
            digitalWrite(RELAY_PIN, HIGH);
            motorOn = false;
            Serial.println("EVENT:PUMP_STOPPED_WET");
        }
        
        displayWetStatus(moisture);
    }
    
    // Send data to webpage
    sendDataToWeb(moisture, soilValue);
    
    delay(500);
}

void countdownSequence(int moisture) {
    // 6-second countdown with buzzer beeps
    for (int i = 6; i > 0; i--) {
        // Check if soil got wet during countdown
        int currentMoisture = map(analogRead(SOIL_PIN), 1023, 0, 0, 100);
        if (currentMoisture >= threshold) {
            countdownActive = false;
            digitalWrite(BUZZER, LOW);
            return;
        }
        
        // Display countdown on LCD
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("! SOIL DRY: ");
        lcd.print(currentMoisture);
        lcd.print("%");
        
        lcd.setCursor(0, 1);
        lcd.print("Motor ON in: ");
        lcd.print(i);
        lcd.print("s");
        
        // Buzzer beep pattern (like stopwatch)
        digitalWrite(BUZZER, HIGH);
        delay(300);
        digitalWrite(BUZZER, LOW);
        delay(700);
        
        // Send countdown to webpage
        Serial.print("COUNTDOWN:");
        Serial.println(i);
    }
    
    // Countdown finished - Turn ON pump
    digitalWrite(BUZZER, LOW);  // Stop buzzer
    digitalWrite(RELAY_PIN, LOW);  // Turn ON pump (active LOW)
    motorOn = true;
    pumpStartTime = millis();
    countdownActive = false;
    
    // Display pump started
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(">>> PUMP ON <<<");
    lcd.setCursor(0, 1);
    lcd.print("Watering...");
    
    Serial.println("EVENT:PUMP_STARTED_AUTO");
}

void displayMotorRunning(int moisture, unsigned long runTime) {
    lcd.setCursor(0, 0);
    lcd.print("PUMP ON  M:");
    lcd.print(moisture);
    lcd.print("%  ");
    
    lcd.setCursor(0, 1);
    lcd.print("Runtime: ");
    lcd.print(runTime);
    lcd.print("s     ");
}

void displayWetStatus(int moisture) {
    lcd.setCursor(0, 0);
    lcd.print("Moisture: ");
    lcd.print(moisture);
    lcd.print("%   ");
    
    lcd.setCursor(0, 1);
    lcd.print("Status: OK      ");
}

void checkSerialCommands() {
    while (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '\n') {
            inputCommand.trim();
            inputCommand.toUpperCase();
            
            if (inputCommand == "PUMP_ON") {
                // Manual pump ON
                digitalWrite(RELAY_PIN, LOW);
                motorOn = true;
                pumpStartTime = millis();
                countdownActive = false;
                digitalWrite(BUZZER, LOW);
                Serial.println("ACK:PUMP_ON_MANUAL");
            } 
            else if (inputCommand == "PUMP_OFF") {
                // Manual pump OFF
                digitalWrite(RELAY_PIN, HIGH);
                motorOn = false;
                Serial.println("ACK:PUMP_OFF_MANUAL");
            }
            else if (inputCommand.startsWith("THRESHOLD:")) {
                int newThreshold = inputCommand.substring(10).toInt();
                if (newThreshold >= 10 && newThreshold <= 90) {
                    threshold = newThreshold;
                    Serial.print("ACK:THRESHOLD:");
                    Serial.println(threshold);
                }
            }
            
            inputCommand = "";
        } else {
            inputCommand += c;
        }
    }
}

void sendDataToWeb(int moisture, int rawValue) {
    Serial.print("MOISTURE:");
    Serial.print(moisture);
    Serial.print(",RAW:");
    Serial.print(rawValue);
    Serial.print(",MOTOR:");
    Serial.println(motorOn ? "ON" : "OFF");
}
