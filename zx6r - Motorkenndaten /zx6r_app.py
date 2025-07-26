#!/usr/bin/env python3
"""
ZX6R Tuning Terminal App
Kawasaki ZX6R 600G Performance & Setup Tracker
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from rich.columns import Columns

class ZX6RApp:
    def __init__(self):
        self.console = Console()
        self.data_file = "zx6r_data.json"
        
        # Standard ZX6R 600G Daten
        self.standard_setup = {
            "hauptduesen": "140/130/130/140",
            "pilotduesen": "12.5er",
            "zuendkerzen": "CR9E",
            "luftfilter": "Original",
            "kraftstoff": "Super Plus (98 Oktan)"
        }
        
        # Dein aktuelles Setup
        self.tuning_setup = {
            "hauptduesen": "135/132.5/132.5/135",
            "pilotduesen": "12.5er (unverändert)",
            "zuendkerzen": "CR10EIX (0.75mm)",
            "luftfilter": "K&N",
            "kraftstoff": "Super Plus (98 Oktan)"
        }
        
        # Standard Leistungsdaten (approximiert)
        self.standard_performance = {
            2000: {"leistung": 25, "drehmoment": 45},
            3000: {"leistung": 45, "drehmoment": 55},
            4000: {"leistung": 65, "drehmoment": 62},
            5000: {"leistung": 80, "drehmoment": 65},
            6000: {"leistung": 92, "drehmoment": 67},
            7000: {"leistung": 102, "drehmoment": 68},
            8000: {"leistung": 106, "drehmoment": 67},
            9000: {"leistung": 109, "drehmoment": 65},
            10000: {"leistung": 111, "drehmoment": 63},
            11000: {"leistung": 112, "drehmoment": 60},
            12000: {"leistung": 110, "drehmoment": 56},
            12500: {"leistung": 107, "drehmoment": 53}
        }
        
        # Geschwindigkeitstabelle
        self.geschwindigkeiten = {
            4000: [28, 42, 58, 72, 88, 102],
            6000: [42, 63, 87, 108, 132, 153],
            8000: [56, 84, 116, 144, 176, 204],
            10000: [70, 105, 145, 180, 220, 255],  # 180 km/h im 4. Gang gemessen
            12000: [84, 120, 174, 216, 264, 306],  # 120 km/h im 2. Gang gemessen
            12500: [87, 125, 181, 225, 275, 319]   # Drehzahlbegrenzer
        }
        
        # Lade gespeicherte Tuning-Daten
        self.tuning_performance = self.load_data()
    
    def load_data(self):
        """Lade gespeicherte Tuning-Daten"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                return data.get('tuning_performance', self.standard_performance.copy())
            except:
                return self.standard_performance.copy()
        return self.standard_performance.copy()
    
    def save_data(self):
        """Speichere Tuning-Daten"""
        data = {
            'tuning_performance': self.tuning_performance,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def show_header(self):
        """Zeige App-Header"""
        header = Text()
        header.append("🏍️  ", style="bold red")
        header.append("ZX6R TUNING TERMINAL", style="bold cyan")
        header.append("  🏍️", style="bold red")
        
        panel = Panel(
            header,
            subtitle="Kawasaki ZX6R 600G Performance Tracker",
            border_style="cyan"
        )
        self.console.print(panel)
        self.console.print()
    
    def show_setup_comparison(self):
        """Zeige Setup-Vergleich"""
        # Standard Setup Tabelle
        standard_table = Table(title="🔧 Standard ZX6R 600G", border_style="blue")
        standard_table.add_column("Komponente", style="cyan")
        standard_table.add_column("Wert", style="white")
        
        for key, value in self.standard_setup.items():
            standard_table.add_row(key.replace("_", " ").title(), value)
        
        # Tuning Setup Tabelle
        tuning_table = Table(title="⚡ Dein Tuning Setup", border_style="green")
        tuning_table.add_column("Komponente", style="cyan")
        tuning_table.add_column("Wert", style="white")
        
        for key, value in self.tuning_setup.items():
            tuning_table.add_row(key.replace("_", " ").title(), value)
        
        # Zeige beide Tabellen nebeneinander
        columns = Columns([standard_table, tuning_table], equal=True, expand=True)
        self.console.print(columns)
        self.console.print()
        
        # Optimierungshinweis
        optimization = Panel(
            "💡 Optimierung: 5er Verkleinerung aller Hauptdüsen für K&N Filter\n"
            "→ Bessere Gasannahme, sauberer Lauf bis 12.500 U/min Begrenzer",
            title="Tuning-Erfolg",
            border_style="green"
        )
        self.console.print(optimization)
    
    def show_performance_table(self):
        """Zeige Leistungsvergleich"""
        table = Table(title="📈 Leistungsvergleich (Standard vs Tuning)")
        table.add_column("Drehzahl", justify="center", style="cyan")
        table.add_column("Standard PS", justify="center", style="blue")
        table.add_column("Standard Nm", justify="center", style="blue")
        table.add_column("Tuning PS", justify="center", style="green")
        table.add_column("Tuning Nm", justify="center", style="green")
        table.add_column("PS Diff", justify="center", style="yellow")
        
        for rpm in sorted(self.standard_performance.keys()):
            std = self.standard_performance[rpm]
            tuning = self.tuning_performance[rpm]
            
            ps_diff = tuning["leistung"] - std["leistung"]
            diff_str = f"+{ps_diff:.1f}" if ps_diff > 0 else f"{ps_diff:.1f}" if ps_diff < 0 else "0.0"
            
            # Markiere Drehzahlbegrenzer
            rpm_str = f"{rpm}" if rpm < 12500 else f"[red]{rpm}[/red] 🚫"
            
            table.add_row(
                rpm_str,
                f"{std['leistung']:.1f}",
                f"{std['drehmoment']:.1f}",
                f"{tuning['leistung']:.1f}",
                f"{tuning['drehmoment']:.1f}",
                diff_str
            )
        
        self.console.print(table)
    
    def show_speed_table(self):
        """Zeige Geschwindigkeitstabelle"""
        table = Table(title="🏁 Geschwindigkeit pro Gang (km/h)")
        table.add_column("Drehzahl", justify="center", style="cyan")
        
        for gang in range(1, 7):
            table.add_column(f"{gang}. Gang", justify="center")
        
        for rpm, speeds in self.geschwindigkeiten.items():
            # Markiere Drehzahlbegrenzer und gemessene Werte
            rpm_str = f"{rpm}"
            if rpm == 12500:
                rpm_str = f"[red]{rpm} 🚫[/red]"
            
            row = [rpm_str]
            for i, speed in enumerate(speeds):
                speed_str = f"{speed}"
                
                # Markiere gemessene Werte
                if (rpm == 12000 and i == 1) or (rpm == 10000 and i == 3):
                    speed_str = f"[green bold]{speed}*[/green bold]"
                # Markiere Drehzahlbegrenzer
                elif rpm == 12500:
                    speed_str = f"[red]{speed}[/red]"
                
                row.append(speed_str)
            
            table.add_row(*row)
        
        self.console.print(table)
        self.console.print("[green]*[/green] = Deine gemessenen Werte | [red]Rot[/red] = Drehzahlbegrenzer")
    
    def edit_tuning_values(self):
        """Bearbeite Tuning-Werte"""
        self.console.print("\n[cyan]📝 Tuning-Werte bearbeiten[/cyan]")
        
        # Zeige verfügbare Drehzahlen
        rpms = list(self.tuning_performance.keys())
        self.console.print(f"Verfügbare Drehzahlen: {', '.join(map(str, rpms))}")
        
        try:
            rpm = int(Prompt.ask("Drehzahl auswählen"))
            if rpm not in rpms:
                self.console.print("[red]❌ Ungültige Drehzahl![/red]")
                return
            
            current = self.tuning_performance[rpm]
            self.console.print(f"\nAktuell bei {rpm} U/min:")
            self.console.print(f"Leistung: {current['leistung']} PS")
            self.console.print(f"Drehmoment: {current['drehmoment']} Nm")
            
            # Neue Werte eingeben
            leistung = Prompt.ask("Neue Leistung (PS)", default=str(current['leistung']))
            drehmoment = Prompt.ask("Neues Drehmoment (Nm)", default=str(current['drehmoment']))
            
            # Werte aktualisieren
            self.tuning_performance[rpm] = {
                'leistung': float(leistung),
                'drehmoment': float(drehmoment)
            }
            
            self.save_data()
            self.console.print("[green]✅ Werte gespeichert![/green]")
            
        except ValueError:
            self.console.print("[red]❌ Ungültige Eingabe![/red]")
    
    def reset_tuning_data(self):
        """Setze Tuning-Daten zurück"""
        if Confirm.ask("Alle Tuning-Daten auf Standard zurücksetzen?"):
            self.tuning_performance = self.standard_performance.copy()
            self.save_data()
            self.console.print("[green]✅ Tuning-Daten zurückgesetzt![/green]")
    
    def show_ascii_graph(self):
        """Zeige einfaches ASCII-Diagramm"""
        self.console.print("\n[cyan]📊 Leistungsdiagramm (ASCII)[/cyan]")
        
        max_power = max(max(p["leistung"] for p in self.standard_performance.values()),
                       max(p["leistung"] for p in self.tuning_performance.values()))
        
        for rpm in sorted(self.standard_performance.keys()):
            std_power = self.standard_performance[rpm]["leistung"]
            tuning_power = self.tuning_performance[rpm]["leistung"]
            
            # Skaliere für ASCII (max 50 Zeichen)
            std_bars = int((std_power / max_power) * 50)
            tuning_bars = int((tuning_power / max_power) * 50)
            
            std_graph = "█" * std_bars
            tuning_graph = "▓" * tuning_bars
            
            self.console.print(f"{rpm:5d}: [blue]{std_graph:50s}[/blue] {std_power:5.1f} PS")
            self.console.print(f"     : [green]{tuning_graph:50s}[/green] {tuning_power:5.1f} PS")
            self.console.print()
    
    def show_menu(self):
        """Zeige Hauptmenü"""
        menu = Table.grid()
        menu.add_column(style="cyan", justify="center")
        menu.add_row("🏍️  ZX6R TUNING MENÜ  🏍️")
        menu.add_row("")
        menu.add_row("[1] Setup-Vergleich anzeigen")
        menu.add_row("[2] Leistungstabelle anzeigen")  
        menu.add_row("[3] Geschwindigkeitstabelle anzeigen")
        menu.add_row("[4] ASCII Leistungsdiagramm")
        menu.add_row("[5] Tuning-Werte bearbeiten")
        menu.add_row("[6] Tuning-Daten zurücksetzen")
        menu.add_row("[7] Alles anzeigen")
        menu.add_row("[0] Beenden")
        
        panel = Panel(menu, border_style="cyan")
        self.console.print(panel)
    
    def run(self):
        """Hauptprogramm"""
        self.console.clear()
        self.show_header()
        
        while True:
            self.show_menu()
            choice = Prompt.ask("\nDeine Wahl", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
            
            self.console.clear()
            self.show_header()
            
            if choice == "0":
                self.console.print("[cyan]Auf Wiedersehen! 🏍️[/cyan]")
                break
            elif choice == "1":
                self.show_setup_comparison()
            elif choice == "2":
                self.show_performance_table()
            elif choice == "3":
                self.show_speed_table()
            elif choice == "4":
                self.show_ascii_graph()
            elif choice == "5":
                self.edit_tuning_values()
            elif choice == "6":
                self.reset_tuning_data()
            elif choice == "7":
                self.show_setup_comparison()
                self.console.print("\n")
                self.show_performance_table()
                self.console.print("\n")
                self.show_speed_table()
            
            if choice != "0":
                self.console.input("\n[dim]Drücke Enter zum Fortfahren...[/dim]")

if __name__ == "__main__":
    # Installation Check
    try:
        from rich.console import Console
    except ImportError:
        print("❌ Rich Library nicht installiert!")
        print("Installiere mit: pip install rich")
        exit(1)
    
    app = ZX6RApp()
    app.run()
