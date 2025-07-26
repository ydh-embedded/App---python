import 'package:flutter/material.dart';

void main() {
  runApp(const NGKAnalyzerApp());
}

class NGKAnalyzerApp extends StatelessWidget {
  const NGKAnalyzerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NGK Zündkerzen Analyzer',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          elevation: 2,
        ),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _controller = TextEditingController();
  AnalysisResult? _result;
  final NGKAnalyzer _analyzer = NGKAnalyzer();

  void _analyzeDesignation() {
    final input = _controller.text.trim();
    if (input.isNotEmpty) {
      setState(() {
        _result = _analyzer.analyzeDesignation(input);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.settings_outlined),
            SizedBox(width: 8),
            Text('NGK Zündkerzen'),
          ],
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Eingabebereich
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '🔍 Zündkerzen-Analyse',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        labelText: 'NGK Bezeichnung',
                        hintText: 'z.B. CR9EK, BR7ES, BPR6ES...',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.search),
                      ),
                      onSubmitted: (_) => _analyzeDesignation(),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _analyzeDesignation,
                        icon: const Icon(Icons.analytics),
                        label: const Text('Analysieren'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.all(16),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Analyse-Ergebnis
            if (_result != null) ...[
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '📋 Analyse von: ${_result!.designation}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                      const Divider(),
                      _buildAnalysisSection(),
                    ],
                  ),
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Navigation Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _showTables(context),
                    icon: const Icon(Icons.table_chart),
                    label: const Text('Tabellen'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _showPhysics(context),
                    icon: const Icon(Icons.science),
                    label: const Text('Physik'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Beispiele
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '💡 Beispiele',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    ...['CR9EK', 'BR7ES', 'BPR6ES', 'BKR6E'].map(
                      (example) => ListTile(
                        dense: true,
                        leading: const Icon(Icons.touch_app, size: 16),
                        title: Text(example),
                        onTap: () {
                          _controller.text = example;
                          _analyzeDesignation();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Gewinde
        _buildInfoRow(
          '🔩 Gewinde',
          _result!.gewinde != null
              ? '${_result!.gewinde} → ${_analyzer.gewindeDaten[_result!.gewinde]?['durchmesser']} (Schlüssel: ${_analyzer.gewindeDaten[_result!.gewinde]?['schluessel']})'
              : 'Nicht erkannt',
          _result!.gewinde != null,
        ),

        // Wärmewert
        _buildWaermewertSection(),

        // Bauart
        _buildInfoRow(
          '⚙️ Bauart',
          _result!.bauart.isNotEmpty
              ? _result!.bauart.map((code) => '$code → ${_analyzer.bauartCodes[code]}').join('\n')
              : 'Standard',
          _result!.bauart.isNotEmpty,
        ),

        // Gewindelänge
        _buildInfoRow(
          '📏 Gewindelänge',
          _result!.gewindelaenge != null
              ? '${_result!.gewindelaenge} → ${_analyzer.gewindelaengeCodes[_result!.gewindelaenge]}'
              : 'Standard',
          _result!.gewindelaenge != null,
        ),

        // Elektroden
        _buildInfoRow(
          '⚡ Elektroden',
          _result!.elektroden.isNotEmpty
              ? _result!.elektroden.map((code) => '$code → ${_analyzer.elektrodenCodes[code]}').join('\n')
              : 'Standard-Elektrode',
          _result!.elektroden.isNotEmpty,
        ),
      ],
    );
  }

  Widget _buildWaermewertSection() {
    if (_result!.waermewert == null) {
      return _buildInfoRow('🌡️ Wärmewert', 'Nicht erkannt', false);
    }

    final waermewertInfo = _analyzer.waermewerte.firstWhere(
      (w) => w['wert'] == _result!.waermewert,
      orElse: () => {},
    );

    if (waermewertInfo.isEmpty) {
      return _buildInfoRow('🌡️ Wärmewert', 'Unbekannter Wärmewert', false);
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🌡️ Wärmewert',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.orange.shade800,
            ),
          ),
          const SizedBox(height: 4),
          Text('${_result!.waermewert} → ${waermewertInfo['typ']} (${waermewertInfo['anwendung']})'),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              '🔬 Wärmeleitwert: ${waermewertInfo['waermeleit']}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String title, String content, bool isHighlighted) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: isHighlighted ? Colors.green.shade50 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isHighlighted ? Colors.green.shade200 : Colors.grey.shade200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: isHighlighted ? Colors.green.shade800 : Colors.grey.shade800,
            ),
          ),
          const SizedBox(height: 4),
          Text(content),
        ],
      ),
    );
  }

  void _showTables(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const TablesPage()),
    );
  }

  void _showPhysics(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const PhysicsPage()),
    );
  }
}

class TablesPage extends StatelessWidget {
  const TablesPage({super.key});

  @override
  Widget build(BuildContext context) {
    final analyzer = NGKAnalyzer();

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Tabellen'),
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.thermostat), text: 'Wärmewerte'),
              Tab(icon: Icon(Icons.settings), text: 'Gewinde'),
              Tab(icon: Icon(Icons.code), text: 'Codes'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            // Wärmewert-Tabelle
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    '🌡️ Wärmewert-Tabelle',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  ...analyzer.waermewerte.map(
                    (item) => Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _getWaermewertColor(item['wert']),
                          child: Text(
                            item['wert'].toString(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        title: Text('${item['typ']} (${item['temp']})'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item['anwendung']),
                            Text(
                              '🔬 ${item['waermeleit']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                          ],
                        ),
                        isThreeLine: true,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Gewinde-Tabelle
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    '🔩 Gewinde-Codes',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  ...analyzer.gewindeDaten.entries.map(
                    (entry) => Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.blue,
                          child: Text(
                            entry.key,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        title: Text(entry.value['durchmesser']!),
                        subtitle: Text('Schlüssel: ${entry.value['schluessel']}'),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Code-Übersicht
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildCodeSection('⚙️ Bauart-Codes', analyzer.bauartCodes),
                  const SizedBox(height: 24),
                  _buildCodeSection('📏 Gewindelänge-Codes', analyzer.gewindelaengeCodes),
                  const SizedBox(height: 24),
                  _buildCodeSection('⚡ Elektroden-Codes (Auswahl)', {
                    'G': analyzer.elektrodenCodes['G']!,
                    'K': analyzer.elektrodenCodes['K']!,
                    'P': analyzer.elektrodenCodes['P']!,
                    'S': analyzer.elektrodenCodes['S']!,
                    'T': analyzer.elektrodenCodes['T']!,
                    'Q': analyzer.elektrodenCodes['Q']!,
                  }),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCodeSection(String title, Map<String, String> codes) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ...codes.entries.map(
          (entry) => Card(
            margin: const EdgeInsets.only(bottom: 4),
            child: ListTile(
              dense: true,
              leading: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    entry.key,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              title: Text(entry.value),
            ),
          ),
        ),
      ],
    );
  }

  Color _getWaermewertColor(int wert) {
    if (wert <= 4) return Colors.red;
    if (wert <= 6) return Colors.orange;
    if (wert <= 9) return Colors.green;
    return Colors.blue;
  }
}

class PhysicsPage extends StatelessWidget {
  const PhysicsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Physikalische Grundlagen'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPhysicsSection(
              '📐 Material und Konstruktion',
              [
                'Isolator-Material: Aluminiumoxid-Keramik (Al2O3)',
                'Material-Wärmeleitfähigkeit: 26-30 W/mK',
                'Effektive Systemwerte: 15-48 W/mK (je nach Geometrie)',
              ],
              Colors.blue,
            ),
            _buildPhysicsSection(
              '🏗️ Geometrie-Einfluss',
              [
                'Heiße Kerzen (2-6): Längere Isolator-Nase',
                '→ Längerer Wärmeweg → Schlechtere Ableitung',
                'Kalte Kerzen (10-14): Kürzere Isolator-Nase',
                '→ Kürzerer Wärmeweg → Bessere Ableitung',
              ],
              Colors.orange,
            ),
            _buildPhysicsSection(
              '🌡️ Temperatur-Unterschiede',
              [
                'Zwischen Wärmewerten: 70-100°C Unterschied',
                'Optimaler Bereich: 500-800°C am Isolator-Ende',
                'Unter 450°C: Verschmutzung/Verrußung',
                'Über 800°C: Glühzündungen/Elektrodenverschleiß',
              ],
              Colors.red,
            ),
            _buildPhysicsSection(
              '⚡ Wärmeableitung',
              [
                '70% über Gewinde/Sitzfläche zum Zylinderkopf',
                '20% über Isolator-Kontakt zum Metallgehäuse',
                '10% über Elektroden und Abgase',
              ],
              Colors.green,
            ),
            _buildPhysicsSection(
              '💡 Wichtige Hinweise',
              [
                'NGK publiziert keine exakten W/mK-Werte',
                'Werte basieren auf technischer Analyse und Geometrie',
                'Effektive Wärmeleitfähigkeit = Material × Geometriefaktor',
              ],
              Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhysicsSection(String title, List<String> points, Color color) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 12),
            ...points.map(
              (point) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      margin: const EdgeInsets.only(top: 6, right: 8),
                      decoration: BoxDecoration(
                        color: color,
                        shape: BoxShape.circle,
                      ),
                    ),
                    Expanded(child: Text(point)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Data Models and Logic

class AnalysisResult {
  final String designation;
  final String? gewinde;
  final List<String> bauart;
  final int? waermewert;
  final String? gewindelaenge;
  final List<String> elektroden;

  AnalysisResult({
    required this.designation,
    this.gewinde,
    required this.bauart,
    this.waermewert,
    this.gewindelaenge,
    required this.elektroden,
  });
}

class NGKAnalyzer {
  final Map<String, Map<String, String>> gewindeDaten = {
    'A': {'durchmesser': '18mm', 'schluessel': '25.4mm'},
    'B': {'durchmesser': '14mm', 'schluessel': '20.8mm'},
    'C': {'durchmesser': '10mm', 'schluessel': '16mm'},
    'D': {'durchmesser': '12mm', 'schluessel': '18mm'},
    'J': {'durchmesser': '12mm (19mm Länge)', 'schluessel': '18mm'},
  };

  final Map<String, String> bauartCodes = {
    'C': 'Kerzen-Schlüsselweite 5/8"',
    'K': 'Kerzen-Schlüsselweite 5/8"; vorstehende Elektrode',
    'M': 'Kompakte Bauform',
    'P': 'Vorgezogene Isolatorspitze',
    'R': 'Mit Entstörwiderstand (5 kOhm)',
    'SD': 'Oberflächenentladung (Wankelmotoren)',
    'U': 'Masseelektrode überdeckt Mittelelektrode halb',
    'Z': 'Mit induktiver Entstörung',
  };

  final Map<String, String> gewindelaengeCodes = {
    'E': '19mm (3/4")',
    'F': 'Konischer Dichtsitz',
    'H': '12.7mm (1/2")',
    'L': '11.2mm (7/16")',
  };

  final Map<String, String> elektrodenCodes = {
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
    'Z': 'Dicke Mittelelektrode (2,9mm)',
  };

  final List<Map<String, dynamic>> waermewerte = [
    {'wert': 2, 'typ': 'Sehr heiß', 'temp': 'Niedrige Motortemp.', 'anwendung': 'Leistungsschwache Motoren', 'waermeleit': '15-18 W/mK'},
    {'wert': 3, 'typ': 'Heiß', 'temp': 'Niedrig-normal', 'anwendung': 'Wenig belastete Motoren', 'waermeleit': '18-21 W/mK'},
    {'wert': 4, 'typ': 'Heiß', 'temp': 'Niedrig-normal', 'anwendung': 'Stadtverkehr, Kurzstrecken', 'waermeleit': '20-23 W/mK'},
    {'wert': 5, 'typ': 'Heiß', 'temp': 'Normal', 'anwendung': 'Standard-Anwendungen', 'waermeleit': '22-25 W/mK'},
    {'wert': 6, 'typ': 'Warm', 'temp': 'Normal', 'anwendung': 'Standard-Anwendungen', 'waermeleit': '24-27 W/mK'},
    {'wert': 7, 'typ': 'Normal', 'temp': 'Standard', 'anwendung': 'Allgemeine Anwendung', 'waermeleit': '26-29 W/mK'},
    {'wert': 8, 'typ': 'Normal/Kalt', 'temp': 'Höher', 'anwendung': 'Winterwetter (bis 15°C)', 'waermeleit': '28-32 W/mK'},
    {'wert': 9, 'typ': 'Kalt', 'temp': 'Hoch', 'anwendung': 'Normal/Regen (bis 20°C)', 'waermeleit': '30-35 W/mK'},
    {'wert': 10, 'typ': 'Kalt', 'temp': 'Hoch', 'anwendung': 'Sommerwetter (ab 20°C)', 'waermeleit': '33-38 W/mK'},
    {'wert': 11, 'typ': 'Sehr kalt', 'temp': 'Sehr hoch', 'anwendung': 'Sportmotoren', 'waermeleit': '35-40 W/mK'},
    {'wert': 12, 'typ': 'Sehr kalt', 'temp': 'Sehr hoch', 'anwendung': 'Leistungsstarke Motoren', 'waermeleit': '38-43 W/mK'},
    {'wert': 13, 'typ': 'Racing', 'temp': 'Extrem', 'anwendung': 'Rennsport, Hochleistung', 'waermeleit': '40-45 W/mK'},
    {'wert': 14, 'typ': 'Racing', 'temp': 'Extrem', 'anwendung': 'Rennzwecke, höchste Belastung', 'waermeleit': '42-48 W/mK'},
  ];

  AnalysisResult? analyzeDesignation(String designation) {
    if (designation.isEmpty) return null;

    final upper = designation.toUpperCase().trim();
    String? gewinde;
    List<String> bauart = [];
    int? waermewert;
    String? gewindelaenge;
    List<String> elektroden = [];

    // Gewinde (erste Stelle)
    if (upper.isNotEmpty && gewindeDaten.containsKey(upper[0])) {
      gewinde = upper[0];
    }

    // Wärmewert extrahieren (Zahlen)
    final waermewertMatch = RegExp(r'(\d+)').firstMatch(upper);
    if (waermewertMatch != null) {
      waermewert = int.parse(waermewertMatch.group(1)!);
    }

    // Bauart-Codes
    for (final code in bauartCodes.keys) {
      if (upper.contains(code)) {
        bauart.add(code);
      }
    }

    // Gewindelänge
    for (final code in gewindelaengeCodes.keys) {
      if (upper.contains(code)) {
        gewindelaenge = code;
        break;
      }
    }

    // Elektroden-Codes (aber nicht die, die schon in bauart sind)
    for (final code in elektrodenCodes.keys) {
      if (upper.contains(code) && !bauart.contains(code)) {
        elektroden.add(code);
      }
    }

    return AnalysisResult(
      designation: upper,
      gewinde: gewinde,
      bauart: bauart,
      waermewert: waermewert,
      gewindelaenge: gewindelaenge,
      elektroden: elektroden,
    );
  }
}
