#!/usr/bin/env python3
"""
ZX6R 1998 Original-Sensoren anzapfen
Temperatursensor + Drehzahlmesser parallel abgreifen
"""

# Arduino/ESP32 Code für Original-Sensor-Anzapfung
arduino_code = '''
/*
ZX6R 1998 Original-Sensor Anzapfung
ESP32 Code für Temperatur + RPM Messung
*/

#include <WiFi.h>
#include <math.h>

// Pin-Definitionen
#define TEMP_ADC_PIN 34    // Temperatur-Signal (ADC1)
#define RPM_PIN 2          // RPM-Signal (Interrupt-fähig)
#define LED_PIN 13         // Status-LED

// RPM Variablen
volatile unsigned long rpmPulseCount = 0;
unsigned long lastRpmTime = 0;
float currentRPM = 0;

// Temperatur Variablen
const float SERIES_RESISTOR = 10000.0;  // 10kΩ Serienwiderstand
const float NOMINAL_RESISTANCE = 2500.0; // NTC bei 25°C
const float NOMINAL_TEMPERATURE = 25.0;
const float B_COEFFICIENT = 3977.0;     // NTC B-Wert (typisch für Motorrad)

void setup() {
  Serial.begin(115200);
  
  // Pin-Konfiguration
  pinMode(RPM_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_ADC_PIN, INPUT);
  
  // RPM Interrupt
  attachInterrupt(digitalPinToInterrupt(RPM_PIN), rpmPulseISR, FALLING);
  
  // ADC Konfiguration für bessere Genauigkeit
  analogReadResolution(12);  // 12-Bit ADC
  analogSetAttenuation(ADC_11db);  // 0-3.3V Bereich
  
  Serial.println("ZX6R Original-Sensor Logger gestartet");
  Serial.println("Temperatur: ADC Pin 34");
  Serial.println("RPM: Interrupt Pin 2");
}

void loop() {
  // Alle 100ms Daten lesen
  static unsigned long lastRead = 0;
  if (millis() - lastRead >= 100) {
    
    // Temperatur lesen
    float temperature = readOriginalTempSensor();
    
    // RPM berechnen
    calculateRPM();
    
    // Status-LED blinken
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    
    // Daten über Serial senden (für Python-Script)
    if (Serial.available() && Serial.readString().indexOf("READ") >= 0) {
      Serial.print("RPM:");
      Serial.print((int)currentRPM);
      Serial.print(",TEMP:");
      Serial.println(temperature, 1);
    }
    
    // Debug-Ausgabe
    if (millis() % 1000 < 100) {  // Jede Sekunde
      Serial.print("Debug - RPM: ");
      Serial.print((int)currentRPM);
      Serial.print(", Temp: ");
      Serial.print(temperature, 1);
      Serial.println("°C");
    }
    
    lastRead = millis();
  }
}

void rpmPulseISR() {
  // Interrupt-Handler für RPM-Pulse
  rpmPulseCount++;
}

void calculateRPM() {
  unsigned long currentTime = millis();
  unsigned long timeDiff = currentTime - lastRpmTime;
  
  if (timeDiff >= 1000) {  // Jede Sekunde berechnen
    // ZX6R: 2 Pulse pro Umdrehung (4-Takt, 4-Zylinder)
    currentRPM = (rpmPulseCount / 2.0) * (60000.0 / timeDiff);
    
    // Plausibilitätsprüfung
    if (currentRPM > 15000) currentRPM = 0;  // Überdrehzahl = Störung
    if (currentRPM < 500) currentRPM = 0;    // Motor steht
    
    // Reset für nächste Berechnung
    rpmPulseCount = 0;
    lastRpmTime = currentTime;
  }
}

float readOriginalTempSensor() {
  // Mehrfach-Messung für Stabilität
  long adcSum = 0;
  for (int i = 0; i < 10; i++) {
    adcSum += analogRead(TEMP_ADC_PIN);
    delayMicroseconds(100);
  }
  float adcValue = adcSum / 10.0;
  
  // ADC zu Spannung (3.3V Referenz, 12-Bit)
  float voltage = (adcValue / 4095.0) * 3.3;
  
  // Spannungsteiler: R_NTC parallel zu 10kΩ
  // V_out = V_in * R_NTC / (R_Series + R_NTC)
  // R_NTC = R_Series * V_out / (V_in - V_out)
  
  float vSupply = 3.3;  // ESP32 Versorgung
  if (voltage >= vSupply * 0.99) return -999;  // Kurzschluss
  if (voltage <= 0.01) return -888;  // Unterbrechung
  
  float resistance = SERIES_RESISTOR * voltage / (vSupply - voltage);
  
  // NTC-Formel: 1/T = 1/T0 + (1/B) * ln(R/R0)
  float steinhart = resistance / NOMINAL_RESISTANCE;
  steinhart = log(steinhart);
  steinhart /= B_COEFFICIENT;
  steinhart += 1.0 / (NOMINAL_TEMPERATURE + 273.15);
  steinhart = 1.0 / steinhart;
  steinhart -= 273.15;  // Kelvin zu Celsius
  
  // Plausibilitätsprüfung
  if (steinhart < -20 || steinhart > 150) {
    return -777;  // Sensor-Fehler
  }
  
  return steinhart;
}
'''

import serial
import time
import json
import math
from datetime import datetime

class OriginalSensorReader:
    """Liest Original ZX6R Sensoren über ESP32"""
    
    def __init__(self, serial_port="/dev/ttyUSB0", baudrate=115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.connection = None
        self.last_temp = 0
        self.last_rpm = 0
        
        self.connect()
    
    def connect(self):
        """Verbinde zu ESP32"""
        try:
            self.connection = serial.Serial(
                self.serial_port, 
                self.baudrate, 
                timeout=2
            )
            time.sleep(3)  # ESP32 Boot-Zeit
            print("✅ ESP32 Original-Sensor Reader verbunden")
            
            # Test-Abfrage
            test_data = self.read_sensors()
            print(f"🧪 Test: {test_data['rpm']} RPM, {test_data['temp']}°C")
            
        except Exception as e:
            print(f"❌ ESP32 Verbindung fehlgeschlagen: {e}")
            print("💡 Prüfe USB-Kabel und Port")
    
    def read_sensors(self) -> dict:
        """Lese Original-Sensoren"""
        if not self.connection:
            return {"rpm": self.last_rpm, "temp": self.last_temp, "status": "disconnected"}
        
        try:
            # Anfrage senden
            self.connection.write(b"READ\n")
            self.connection.flush()
            
            # Antwort lesen (Timeout 2s)
            response = self.connection.readline().decode().strip()
            
            if response and "RPM:" in response and "TEMP:" in response:
                # Parse Response: "RPM:5500,TEMP:85.5"
                parts = response.split(",")
                
                rpm_part = [p for p in parts if p.startswith("RPM:")][0]
                temp_part = [p for p in parts if p.startswith("TEMP:")][0]
                
                rpm = int(rpm_part.split(":")[1])
                temp = float(temp_part.split(":")[1])
                
                # Fehler-Codes prüfen
                if temp < -500:
                    temp_status = "sensor_error"
                    temp = self.last_temp  # Letzten gültigen Wert verwenden
                else:
                    temp_status = "ok"
                    self.last_temp = temp
                
                if rpm < 500:
                    rpm_status = "idle_or_error"
                else:
                    rpm_status = "ok"
                    self.last_rpm = rpm
                
                return {
                    "rpm": rpm,
                    "temp": temp,
                    "rpm_status": rpm_status,
                    "temp_status": temp_status,
                    "status": "connected",
                    "raw_response": response
                }
            
            else:
                print(f"⚠️ Unerwartete Antwort: {response}")
                return {"rpm": self.last_rpm, "temp": self.last_temp, "status": "parse_error"}
                
        except Exception as e:
            print(f"❌ Sensor-Lesefehler: {e}")
            return {"rpm": self.last_rpm, "temp": self.last_temp, "status": "read_error"}
    
    def start_continuous_logging(self, duration_minutes=10):
        """Starte kontinuierliche Aufzeichnung"""
        
        log_file = f"zx6r_original_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        print(f"📊 Starte Original-Sensor Logging: {duration_minutes} min")
        print(f"📁 Datei: {log_file}")
        
        # CSV Header
        with open(log_file, 'w') as f:
            f.write("timestamp,rpm,temp,rpm_status,temp_status\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                timestamp = time.time()
                data = self.read_sensors()
                
                # Live-Anzeige
                status_indicator = "🟢" if data["status"] == "connected" else "🔴"
                print(f"\r{status_indicator} {data['rpm']:4d} RPM | {data['temp']:5.1f}°C | {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}", end="")
                
                # CSV schreiben
                with open(log_file, 'a') as f:
                    f.write(f"{timestamp},{data['rpm']},{data['temp']},{data['rpm_status']},{data['temp_status']}\n")
                
                time.sleep(0.1)  # 10Hz
                
        except KeyboardInterrupt:
            print("\n🛑 Logging gestoppt")
        
        print(f"\n📁 Daten gespeichert: {log_file}")
        return log_file

# Schaltplan als Kommentar
wiring_diagram = '''
🔌 VERKABELUNG ZX6R ORIGINAL-SENSOREN:

TEMPERATURSENSOR (Kühler):
┌─────────────────────┐    ┌─────────────┐
│  Original ECU/Tacho │    │    ESP32    │
│                     │    │             │
│  Temp-Signal ●──────┼────┤ Pin 34 (ADC)│
│  (Grün/Gelb)        │    │             │
│                     │    │ 10kΩ ───────┤
│  GND ●──────────────┼────┤ GND         │
└─────────────────────┘    └─────────────┘

WICHTIG: 10kΩ Serienwiderstand zum Schutz!

DREHZAHLMESSER (Tacho):
┌─────────────────────┐    ┌─────────────┐
│   Original Tacho    │    │    ESP32    │
│                     │    │             │
│  +12V (Rot) ●───────┼────┤ VIN (12V)   │
│                     │    │             │
│  RPM-Signal ●───────┼────┤ Pin 2 (INT) │
│  (Weiß/Gelb)        │    │             │
│                     │    │ 10kΩ ───────┤ (Pull-up)
│  GND (Schwarz) ●────┼────┤ GND         │
└─────────────────────┘    └─────────────┘

VORSICHT: 
- Niemals Original-Kabel durchtrennen!
- Nur parallel anzapfen mit Y-Kabeln
- Spannungsteiler für 12V→3.3V verwenden
- Absicherung mit 1A Sicherung
'''

def main():
    """Hauptprogramm für Original-Sensor Anzapfung"""
    
    print("🏍️ ZX6R Original-Sensor Logger")
    print("🔧 Anzapfung Temperatur + RPM")
    print("=" * 40)
    
    print(wiring_diagram)
    
    # Sensor-Reader starten
    try:
        reader = OriginalSensorReader()
        
        # Test-Lesung
        test_data = reader.read_sensors()
        print(f"\n🧪 Sensor-Test:")
        print(f"   RPM: {test_data['rpm']} ({test_data.get('rpm_status', 'unknown')})")
        print(f"   Temperatur: {test_data['temp']}°C ({test_data.get('temp_status', 'unknown')})")
        print(f"   Verbindung: {test_data['status']}")
        
        if test_data['status'] == 'connected':
            duration = int(input("\nAufzeichnungsdauer (Minuten): "))
            reader.start_continuous_logging(duration)
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        print("\n💡 Prüfe:")
        print("   - ESP32 USB-Verbindung")
        print("   - Original-Sensor Verkabelung")
        print("   - Spannungsteiler korrekt?")

if __name__ == "__main__":
    main()
