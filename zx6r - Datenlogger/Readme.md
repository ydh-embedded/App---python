# ZX6R Datenlogger
## 🚀 Einfache Anleitung für ZX6R Datenlogger mit ESP32
### 📋 Voraussetzungen



🔌 ANGEPASSTE EINKAUFSLISTE (viel günstiger!):
#### HAUPTKOMPONENTEN (~25€):
✅ ESP32 DevKit V1:              ~15€
✅ Widerstände-Set (10kΩ, 1kΩ):   ~3€
✅ Y-Kabel Automotive:            ~7€
❌ DS18B20 Temperatursensor    (NICHT NÖTIG!)
❌ Hall-Sensor                 (NICHT NÖTIG!)
#### VERKABELUNG (~15€):
✅ Spannungsteiler-Widerstände 10kΩ (5 Stück)
✅ Y-Kabel 3-adrig (für RPM-Anzapfung)
✅ Y-Kabel 2-adrig (für Temperatur-Anzapfung)
✅ Automotive-Kabel 0.75mm² (3m)
✅ Lötkolben + Lötzinn
✅ Schrumpfschlauch-Set
#### GEHÄUSE (~10€):
✅ Kleines wasserdichtes Gehäuse 80x50x30mm
✅ Kabelverschraubungen M8 (2 Stück)
#### STROMVERSORGUNG (~8€):
✅ 12V→5V Buck Converter (LM2596)
✅ 1A Flachsicherung + Halter
#### ⚡ VERKABELUNGSPLAN:
##### 🌡️ Temperatursensor anzapfen:
```ps
Original Kabel: Grün/Gelb + Schwarz
├─ Grün/Gelb → Y-Kabel → Original ECU
│                    └─ 10kΩ → ESP32 Pin 34
└─ Schwarz → Y-Kabel → Original ECU
                   └─ ESP32 GND
```
##### 🔄 RPM-Signal anzapfen:
```ps

Original Tacho (3 Kabel):
├─ Rot (+12V) → Y-Kabel → Original Tacho
│                      └─ Buck Converter → ESP32 VIN
├─ Weiß/Gelb (RPM) → Y-Kabel → Original Tacho  
│                           └─ 10kΩ → ESP32 Pin 2
└─ Schwarz (GND) → Y-Kabel → Original Tacho
                          └─ ESP32 GND
```
#### 🛒 KONKRETE BESTELLUNG:
Amazon (~40€ total):
📦 "ESP32 WROOM-32 Development Board"     ~15€
📦 "Automotive Y-Kabel Sortiment"        ~12€  
📦 "Widerstand Sortiment 1/4W"           ~5€
📦 "LM2596 DC-DC Step Down 12V 5V"       ~5€
📦 "Wasserdichtes Gehäuse 80x50mm"       ~8€
#### Baumarkt/Elektronikladen (~15€):
🔧 Lötkolben 40W                         ~8€
🔌 Lötzinn + Schrumpfschlauch            ~7€