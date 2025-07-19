#!/usr/bin/env python3
"""
NGK Zündkerzen Terminal-Analyzer
Analysiert NGK Zündkerzen-Bezeichnungen und zeigt alle relevanten Informationen an.
"""

import re
import os
from typing import Dict, List, Optional, Tuple

class NGKAnalyzer:
    def __init__(self):
        self.gewinde_daten = {
            'A': {'durchmesser': '18mm', 'schluessel': '25.4mm'},
            'B': {'durchmesser': '14mm', 'schluessel': '20.8mm'},
            'C': {'durchmesser': '10mm', 'schluessel': '16mm'},
            'D': {'durchmesser': '12mm', 'schluessel': '18mm'},
            'J': {'durchmesser': '12mm (19mm Länge)', 'schluessel': '18mm'}
        }
        
        self.bauart_codes = {
            'C': 'Kerzen-Schlüsselweite 5/8"',
            'K': 'Kerzen-Schlüsselweite 5/8"; vorstehende Elektrode',
            'M': 'Kompakte Bauform',
            'P': 'Vorgezogene Isolatorspitze',
            'R': 'Mit Entstörwiderstand (5 kOhm)',
            'SD': 'Oberflächenentladung (Wankelmotoren)',
            'U': 'Masseelektrode überdeckt Mittelelektrode halb',
            'Z': 'Mit induktiver Entstörung'
        }
        
        self.gewindelaenge_codes = {
            'E': '19mm (3/4")',
            'F': 'Konischer Dichtsitz',
            'H': '12.7mm (1/2")',
            'L': '11.2mm (7/16")'
        }
        
        self.elektroden_codes = {
            'A': 'Sonderbauform',
            'B': 'Sonderbauform (Honda CVCC)',
            'C': 'Niedrig-winkelig geschliffene Elektrode',
            'G': 'Stift-Mittelelektrode aus Nickellegierung',
            'GV': 'Gold-Palladium-Mittelelektrode (Rennversion)',
            'H': 'Teilgewinde',
            'K': 'Doppel-Masseelektrode (Toyota, BMW)',
            'L': 'Halber Wärmewert',
            'LM': 'Kompaktbauform für Rasenmäher',
            'M': 'Doppel-Masseelektrode (Wankelmotoren)',
            'N': 'Spezial-Seitenelektrode',
            'P': 'Premium-Platin-Mittelelektrode',
            'Q': 'Vierfach-Masseelektrode',
            'R': 'Delta-geschliffene Spezial-Mittelelektrode (BMW)',
            'S': 'Standard-Mittelelektrode aus Kupfer (2,6mm)',
            'T': 'Dreifach-Masseelektrode',
            'U': 'Halbflächige Entladung',
            'V': 'Stift-Gold-Palladium-Mittelelektrode (1,0mm)',
            'VX': 'Hochleistungs-Platin-Mittelelektrode (0,8mm)',
            'W': 'Tungsten-Elektrode',
            'X': 'Booster-Abstand',
            'Y': 'V-förmig geschlitzte Mittelelektrode',
            'Z': 'Dicke Mittelelektrode (2,9mm)'
        }
        
        self.waermewerte = [
            {'wert': 2, 'typ': 'Sehr heiß', 'temp': 'Niedrige Motortemp.', 'anwendung': 'Leistungsschwache Motoren'},
            {'wert': 3, 'typ': 'Heiß', 'temp': 'Niedrig-normal', 'anwendung': 'Wenig belastete Motoren'},
            {'wert': 4, 'typ': 'Heiß', 'temp': 'Niedrig-normal', 'anwendung': 'Stadtverkehr, Kurzstrecken'},
            {'wert': 5, 'typ': 'Heiß', 'temp': 'Normal', 'anwendung': 'Standard-Anwendungen'},
            {'wert': 6, 'typ': 'Warm', 'temp': 'Normal', 'anwendung': 'Standard-Anwendungen'},
            {'wert': 7, 'typ': 'Normal', 'temp': 'Standard', 'anwendung': 'Allgemeine Anwendung'},
            {'wert': 8, 'typ': 'Normal/Kalt', 'temp': 'Höher', 'anwendung': 'Winterwetter (bis 15°C)'},
            {'wert': 9, 'typ': 'Kalt', 'temp': 'Hoch', 'anwendung': 'Normal/Regen (bis 20°C)'},
            {'wert': 10, 'typ': 'Kalt', 'temp': 'Hoch', 'anwendung': 'Sommerwetter (ab 20°C)'},
            {'wert': 11, 'typ': 'Sehr kalt', 'temp': 'Sehr hoch', 'anwendung': 'Sportmotoren'},
            {'wert': 12, 'typ': 'Sehr kalt', 'temp': 'Sehr hoch', 'anwendung': 'Leistungsstarke Motoren'},
            {'wert': 13, 'typ': 'Racing', 'temp': 'Extrem', 'anwendung': 'Rennsport, Hochleistung'},
            {'wert': 14, 'typ': 'Racing', 'temp': 'Extrem', 'anwendung': 'Rennzwecke, höchste Belastung'}
        ]

    def clear_screen(self):
        """Bildschirm löschen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Header ausgeben"""
        print("=" * 70)
        print("🔧 NGK ZÜNDKERZEN TERMINAL-ANALYZER 🔧")
        print("=" * 70)
        print()

    def analyze_designation(self, designation: str) -> Dict:
        """Analysiert eine NGK Zündkerzen-Bezeichnung"""
        if not designation:
            return None
            
        upper = designation.upper().strip()
        result = {
            'designation': upper,
            'gewinde': None,
            'bauart': [],
            'waermewert': None,
            'gewindelaenge': None,
            'elektroden': [],
            'abstand': None
        }

        # Gewinde (erste Stelle)
        if upper and upper[0] in self.gewinde_daten:
            result['gewinde'] = upper[0]

        # Wärmewert extrahieren (Zahlen)
        waermewert_match = re.search(r'(\d+)', upper)
        if waermewert_match:
            result['waermewert'] = int(waermewert_match.group(1))

        # Bauart-Codes
        for code in self.bauart_codes:
            if code in upper:
                result['bauart'].append(code)

        # Gewindelänge
        for code in self.gewindelaenge_codes:
            if code in upper:
                result['gewindelaenge'] = code

        # Elektroden-Codes (aber nicht die, die schon in bauart sind)
        for code in self.elektroden_codes:
            if code in upper and code not in result['bauart']:
                result['elektroden'].append(code)

        return result

    def print_analysis(self, analysis: Dict):
        """Gibt die Analyse formatiert aus"""
        print(f"📋 ANALYSE VON: {analysis['designation']}")
        print("-" * 50)
        
        # Gewinde
        print("🔩 GEWINDE:")
        if analysis['gewinde'] and analysis['gewinde'] in self.gewinde_daten:
            data = self.gewinde_daten[analysis['gewinde']]
            print(f"   {analysis['gewinde']} → {data['durchmesser']} (Schlüssel: {data['schluessel']})")
        else:
            print("   ❌ Nicht erkannt")
        print()
        
        # Wärmewert
        print("🌡️  WÄRMEWERT:")
        if analysis['waermewert']:
            waermewert_info = next((w for w in self.waermewerte if w['wert'] == analysis['waermewert']), None)
            if waermewert_info:
                print(f"   {analysis['waermewert']} → {waermewert_info['typ']} ({waermewert_info['anwendung']})")
            else:
                print(f"   {analysis['waermewert']} → Unbekannter Wärmewert")
        else:
            print("   ❌ Nicht erkannt")
        print()
        
        # Bauart-Features
        print("⚙️  BAUART-FEATURES:")
        if analysis['bauart']:
            for code in analysis['bauart']:
                print(f"   {code} → {self.bauart_codes[code]}")
        else:
            print("   Standard (keine besonderen Features)")
        print()
        
        # Gewindelänge
        print("📏 GEWINDELÄNGE:")
        if analysis['gewindelaenge']:
            print(f"   {analysis['gewindelaenge']} → {self.gewindelaenge_codes[analysis['gewindelaenge']]}")
        else:
            print("   Standard")
        print()
        
        # Elektroden
        print("⚡ ELEKTRODEN:")
        if analysis['elektroden']:
            for code in analysis['elektroden']:
                print(f"   {code} → {self.elektroden_codes[code]}")
        else:
            print("   Standard-Elektrode")
        print()

    def print_waermewert_table(self):
        """Gibt die Wärmewert-Tabelle aus"""
        print("📊 WÄRMEWERT-TABELLE")
        print("=" * 80)
        print(f"{'Wert':<4} | {'Typ':<12} | {'Temperatur':<15} | {'Anwendung':<35}")
        print("-" * 80)
        
        for item in self.waermewerte:
            print(f"{item['wert']:<4} | {item['typ']:<12} | {item['temp']:<15} | {item['anwendung']:<35}")
        print()

    def print_gewinde_table(self):
        """Gibt die Gewinde-Tabelle aus"""
        print("🔩 GEWINDE-CODES")
        print("=" * 50)
        print(f"{'Code':<4} | {'Durchmesser':<20} | {'Schlüssel':<10}")
        print("-" * 50)
        
        for code, data in self.gewinde_daten.items():
            print(f"{code:<4} | {data['durchmesser']:<20} | {data['schluessel']:<10}")
        print()

    def print_codes_overview(self):
        """Gibt eine Übersicht aller Codes aus"""
        print("📖 CODE-ÜBERSICHT")
        print("=" * 50)
        
        print("⚙️ BAUART-CODES:")
        for code, desc in self.bauart_codes.items():
            print(f"   {code:<3} → {desc}")
        print()
        
        print("📏 GEWINDELÄNGE-CODES:")
        for code, desc in self.gewindelaenge_codes.items():
            print(f"   {code:<3} → {desc}")
        print()
        
        print("⚡ ELEKTRODEN-CODES (Auswahl):")
        important_codes = ['G', 'K', 'P', 'S', 'T', 'Q', 'V', 'VX']
        for code in important_codes:
            if code in self.elektroden_codes:
                print(f"   {code:<3} → {self.elektroden_codes[code]}")
        print(f"   ... und {len(self.elektroden_codes) - len(important_codes)} weitere")
        print()

    def show_menu(self):
        """Zeigt das Hauptmenü"""
        print("📋 OPTIONEN:")
        print("1. Zündkerze analysieren")
        print("2. Wärmewert-Tabelle anzeigen") 
        print("3. Gewinde-Codes anzeigen")
        print("4. Code-Übersicht anzeigen")
        print("5. Beispiele anzeigen")
        print("0. Beenden")
        print()

    def show_examples(self):
        """Zeigt Beispiele"""
        print("💡 BEISPIELE FÜR NGK BEZEICHNUNGEN:")
        print("=" * 50)
        examples = [
            ("CR9EK", "10mm Gewinde, Entstörwiderstand, Wärmewert 9, 19mm Länge, Doppelelektrode"),
            ("BR7ES", "14mm Gewinde, Entstörwiderstand, Wärmewert 7, 19mm Länge, Standard"),
            ("BPR6ES", "14mm Gewinde, Platin + Entstörwiderstand, Wärmewert 6, 19mm, Standard"),
            ("BKR6E", "14mm Gewinde, Doppelelektrode, Wärmewert 6, 19mm Länge"),
            ("CR8E", "10mm Gewinde, Wärmewert 8, 19mm Länge")
        ]
        
        for designation, description in examples:
            print(f"   {designation:<8} → {description}")
        print()

    def run(self):
        """Hauptprogramm-Schleife"""
        while True:
            self.clear_screen()
            self.print_header()
            self.show_menu()
            
            try:
                choice = input("Wähle eine Option (0-5): ").strip()
                
                if choice == '0':
                    print("\n👋 Auf Wiedersehen!")
                    break
                    
                elif choice == '1':
                    self.clear_screen()
                    self.print_header()
                    designation = input("🔍 NGK Bezeichnung eingeben (z.B. CR9EK): ").strip()
                    
                    if designation:
                        analysis = self.analyze_designation(designation)
                        if analysis:
                            print()
                            self.print_analysis(analysis)
                        else:
                            print("❌ Ungültige Eingabe!")
                    else:
                        print("❌ Keine Eingabe!")
                    
                    input("\n⏎ Drücke Enter um fortzufahren...")
                    
                elif choice == '2':
                    self.clear_screen()
                    self.print_header()
                    self.print_waermewert_table()
                    input("⏎ Drücke Enter um fortzufahren...")
                    
                elif choice == '3':
                    self.clear_screen()
                    self.print_header()
                    self.print_gewinde_table()
                    input("⏎ Drücke Enter um fortzufahren...")
                    
                elif choice == '4':
                    self.clear_screen()
                    self.print_header()
                    self.print_codes_overview()
                    input("⏎ Drücke Enter um fortzufahren...")
                    
                elif choice == '5':
                    self.clear_screen()
                    self.print_header()
                    self.show_examples()
                    input("⏎ Drücke Enter um fortzufahren...")
                    
                else:
                    print("❌ Ungültige Auswahl!")
                    input("⏎ Drücke Enter um fortzufahren...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Programm beendet!")
                break
            except Exception as e:
                print(f"❌ Fehler: {e}")
                input("⏎ Drücke Enter um fortzufahren...")

def main():
    """Hauptfunktion"""
    print("🚀 NGK Zündkerzen Terminal-Analyzer wird gestartet...")
    print("   Lade Datenbank...")
    
    analyzer = NGKAnalyzer()
    
    print("   ✅ Bereit!")
    input("   ⏎ Drücke Enter um zu starten...")
    
    analyzer.run()

if __name__ == "__main__":
    main()
