![Logo](images/heading.svg)

[🇬🇧 English](README.md) | 🇩🇪 **Deutsch**

## Energiezähler-Offset-Robot für Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![release](https://img.shields.io/github/v/release/arboeh/enerABot?display_name=tag)](https://github.com/arboeh/enerABot/releases/latest)
[![codecov](https://codecov.io/gh/arboeh/enerABot/branch/main/graph/badge.svg)](https://codecov.io/gh/arboeh/enerABot)
[![CI](https://github.com/arboeh/enerABot/workflows/CI/badge.svg)](https://github.com/arboeh/enerABot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/enerABot/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/enerABot/graphs/commit-activity)

> **⚠️ Beta-Release** - enerABot 0.1.0-beta ist funktionsfähig, wird aber aktiv weiterentwickelt.
> Breaking Changes vor 1.0.0 sind möglich. Bitte Probleme auf GitHub melden.

**enerABot** bringt deinen physischen Zählerstand elektronisch in Home
Assistant - kein manuelles Ablesen mehr nötig. Die App nutzt deine
bestehenden totalen (kumulativen) Netzbezugs- und/oder Netzeinspeisungs-
Sensoren und gleicht sie einmalig über die UI an den realen Zählerstand an,
sodass der angezeigte Wert immer mit dem physischen Zähler übereinstimmt.

Das ist immer dann hilfreich, wenn der kumulative Zählerstand eines Sensors
nicht mit dem physischen Zähler übereinstimmt - z. B. nach einem
Wechselrichter-Tausch, einer Integrationsmigration, einem Sensor-Reset, oder
weil die Quellintegration einfach bei null statt beim tatsächlichen
Zählerstand zu zählen begonnen hat.

enerABot funktioniert mit **jedem** totalen/kumulativen Netzsensor - unabhängig
von Hersteller oder Integration. Ein Beispiel ist
[huABus](https://github.com/arboeh/huABus), das für Huawei-Solarwechselrichter
`sensor.huawei_solar_inverter_grid_energy_exported` und
`sensor.huawei_solar_inverter_grid_energy_imported` bereitstellt - aber jeder
andere totale Bezugs-/Einspeisesensor funktioniert genauso gut.

## Funktionen

- 🔢 **Offset-Berechnung** - realen Zählerstand eingeben, enerABot berechnet und speichert den Offset automatisch
- ⚡ **Bezug und/oder Einspeisung** - nur einen Bezugssensor, nur einen Einspeisesensor oder beide konfigurieren - je nachdem, was dein Setup bereitstellt
- 🔌 **Quellenunabhängig** - funktioniert mit jedem totalen/kumulativen Energiesensor (Einweg- oder Zweiwegzähler)
- 🧾 **OBIS-Code-Metadaten** - optional jeden Zähler mit seinem OBIS-Code kennzeichnen (z. B. `1.8.2`, `2.8.2`), nach IEC 62056-6-1
- 🆔 **Zähler-ID** - optional die Seriennummer/Kennung des physischen Zählers je Richtung speichern
- 💶 **Tarifpreis (optional)** - EUR/kWh-Preis je Richtung für zukünftige Kostenberechnung speichern
- 🗓️ **Ablesezyklus** - Zählerpaar optional als täglich, monatlich oder manuell abzulesend markieren
- 🧮 **Coordinator-basierte Updates** - Offsets werden bei jedem Sensor-Update live angewendet
- 🛡️ **Robustes Fehlerverhalten** - nicht verfügbare/unbekannte Quellsensoren zerstören keine Statistik (`TOTAL_INCREASING` bleibt intakt)
- 🕒 **Letzte Korrektur nachvollziehbar** - jeder Sensor zeigt `last_correction` und `offset` als Attribute, zusätzlich optional `obis_code`, `meter_id` und `tariff_price`, falls konfiguriert
- 🛠️ **HA-Services** - `set_energy_meter_import`, `set_energy_meter_export` für Automatisierungen
- 🌍 **Mehrsprachig** - Englische und deutsche Übersetzungen enthalten
- **🧪 Umfangreiche Testabdeckung**
  - Unit-Tests für **Config Flow, Options Flow, Coordinator, Init, Sensoren**
  - CI-Tests für **Python 3.11 und 3.12**

## Voraussetzungen

- Home Assistant **2024.1+**
- Mindestens ein bestehender totaler/kumulativer Energiesensor (Bezug
  und/oder Einspeisung) mit numerischem Zustand - z. B. aus einer
  Smart-Meter-Integration, einem Solarwechselrichter oder MQTT-Sensor. Beide
  Sensoren sind einzeln optional, aber mindestens einer muss konfiguriert sein.

## Funktionsweise

1. Du fügst ein Zählerpaar über den Config Flow hinzu und konfigurierst einen
   Bezugssensor, einen Einspeisesensor oder beide
2. enerABot erstellt für jede konfigurierte Richtung einen passenden Sensor,
   der den Quellsensor plus gespeicherten Offset spiegelt
3. Beim Ablesen deines physischen Zählers öffnest du die **Optionen** der
   Integration und gibst den realen Zählerstand für Bezug oder Einspeisung ein
4. enerABot berechnet `offset = realer_zählerstand - aktueller_sensorwert` und speichert ihn
5. Ab sofort meldet der enerABot-Sensor `quellwert + offset` - stets passend
   zum physischen Zähler, ohne dass du erneut ablesen musst
6. Optional kannst du jedes Zählerpaar mit einem OBIS-Code, einer Zähler-ID,
   einem Tarifpreis und einem Ablesezyklus versehen - entweder direkt bei
   der Einrichtung oder später über die Optionen. Diese Felder sind rein
   beschreibende Metadaten und beeinflussen die Offset-Berechnung nicht

## Installation via HACS

1. HACS öffnen → **Integrationen**
2. **⋮ → Benutzerdefinierte Repositories** klicken
3. `https://github.com/arboeh/enerABot` als Typ **Integration** hinzufügen
4. Nach **enerABot** suchen und installieren
5. Home Assistant neu starten

## Manuelle Installation

1. `custom_components/enerabot/` in den Ordner `config/custom_components/` kopieren
2. Home Assistant neu starten

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach **enerABot** suchen
3. Bezugssensor, Einspeisesensor oder beide auswählen und dem Zählerpaar einen Namen geben
4. Optional: initialen Zählerstand, Zähler-ID, OBIS-Code, Tarifpreis und
   Ablesezyklus je konfigurierter Richtung angeben
5. Das Paar wird validiert und automatisch hinzugefügt

> Alle Metadatenfelder (Zähler-ID, OBIS-Code, Tarifpreis, Ablesezyklus) sind
> optional und können später über die **Optionen** ergänzt oder geändert werden.

## Verwendung

Nach der Einrichtung öffnest du über **Konfigurieren** die Optionen, um Offsets und Metadaten zu korrigieren:

| Option                            | Beschreibung                                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------------------------|
| 🔢 Bezugszähler korrigieren        | Realen Zählerstand für Bezug (1.8.0) eingeben und optional Zähler-ID, OBIS-Code, Preis aktualisieren |
| 🔢 Einspeisungszähler korrigieren  | Realen Zählerstand für Einspeisung (2.8.0) eingeben und optional Zähler-ID, OBIS-Code, Preis aktualisieren |

## Entitäten

Für jede konfigurierte Richtung erstellt enerABot:

| Entität                           | Typ    | Beschreibung                                   |
| ---------------------------------- | ------ | ------------------------------------------------|
| `sensor.<name>_import`            | Sensor | Bezugswert mit angewendetem Offset              |
| `sensor.<name>_export`            | Sensor | Einspeisewert mit angewendetem Offset           |

Beide Sensoren zeigen folgende Attribute:

| Attribut                  | Beschreibung                                                  |
| --------------------------- | ---------------------------------------------------------- |
| `offset`                  | Aktuell gespeicherter Offset-Wert                            |
| `last_correction`         | Zeitstempel der letzten Zählerstand-Korrektur                 |
| `raw_sensor`              | Entity-ID des zugrunde liegenden Quellsensors                 |
| `meter_id` (optional)     | Seriennummer/Kennung des physischen Zählers, falls konfiguriert |
| `obis_code` (optional)    | OBIS-Code des Registers, falls konfiguriert (z. B. `1.8.2`)   |
| `tariff_price` (optional) | Gespeicherter EUR/kWh-Preis, falls konfiguriert                |

## Services

### `enerabot.set_energy_meter_import`

```yaml
service: enerabot.set_energy_meter_import
data:
  entity_id: sensor.mein_bezug
  meter_value: 1234.5
```

### `enerabot.set_energy_meter_export`

```yaml
service: enerabot.set_energy_meter_export
data:
  entity_id: sensor.meine_einspeisung
  meter_value: 567.8
```

## Bekannte Einschränkungen (0.1.0-beta)

- Nur ein Bezugs- und ein Einspeisesensor pro Zählerpaar
- Keine Offset-Historie; nur der aktuellste Offset und Korrekturzeitpunkt werden gespeichert
- Keine Mehrtarif-Aufteilung (HT/NT) als eigene Sensoren - `tariff_price` und `reading_cycle` sind bisher reine Metadaten, noch ohne automatische Kosten- oder Zykluslogik

## Geplante Funktionen (zukünftige Releases)

- 🧾 **Mehrtarif-Unterstützung**
  Eigene Sensor-Slots für HT/NT-Register je Richtung
- 💶 **Automatische Kostenberechnung**
  Nutzung des gespeicherten `tariff_price` zur laufenden Kostenermittlung
- 📊 **Offset-Historie**
  Alle vergangenen Korrekturen nachvollziehbar machen, nicht nur die letzte
- 📱 **Lovelace-Karte**
  Eigene Karte für schnelle Zählerkorrektur ohne Öffnen der Optionen
- 🔔 **Abweichungs-Benachrichtigungen**
  Warnung, wenn der berechnete Offset einen konfigurierbaren Schwellenwert übersteigt
- 🔄 **Generalisierte Sensor-Unterstützung**
  Unterstützung beliebiger `total_increasing`-Sensoren mit wählbarer Einheit, nicht nur Energie

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Lizenz

MIT © 2026 [arboeh](https://github.com/arboeh) - siehe [LICENSE](LICENSE)