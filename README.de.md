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

> **⚠️ Beta-Release** - enerABot 0.2.0-beta ist funktionsfähig, wird aber aktiv weiterentwickelt.
> Breaking Changes vor 1.0.0 sind möglich. Bitte Probleme auf GitHub melden.

**enerABot** bringt deinen physischen Zählerstand elektronisch in Home
Assistant - kein manuelles Ablesen mehr nötig. Die App nutzt einen
bestehenden totalen (kumulativen) Netzsensor und gleicht ihn einmalig über
die UI an den realen Zählerstand an, sodass der angezeigte Wert immer mit
dem physischen Zähler übereinstimmt.

Jeder enerABot-Eintrag repräsentiert **ein physisches Zählerregister** - du
wählst den Quellsensor und den passenden OBIS-Code (z. B. `1.8.2` für Bezug,
`2.8.2` für Einspeisung), und enerABot erkennt daraus automatisch, ob es sich
um einen Bezugs- oder Einspeisezähler handelt. Wenn du sowohl einen
Bezugs- als auch einen Einspeisesensor hast, fügst du enerABot einfach
zweimal hinzu - einmal je Richtung.

## Funktionen

- 🔢 **Offset-Berechnung** - realen Zählerstand eingeben, enerABot berechnet und speichert den Offset automatisch
- 🧾 **OBIS-Code bestimmt die Richtung** - OBIS-Code auswählen (z. B. `1.8.2`, `2.8.2`), enerABot erkennt automatisch Bezug oder Einspeisung, nach IEC 62056-6-1
- 🔌 **Quellenunabhängig** - funktioniert mit jedem totalen/kumulativen Energiesensor
- 🆔 **Zähler-ID** - optional die Seriennummer/Kennung des physischen Zählers speichern
- 💶 **Tarifpreis (optional)** - EUR/kWh-Preis für zukünftige Kostenberechnung speichern
- 🗓️ **Ablesezyklus** - Zähler optional als täglich, monatlich oder manuell abzulesend markieren
- 🧮 **Coordinator-basierte Updates** - Offsets werden bei jedem Sensor-Update live angewendet
- 🛡️ **Robustes Fehlerverhalten** - nicht verfügbare/unbekannte Quellsensoren zerstören keine Statistik (`TOTAL_INCREASING` bleibt intakt)
- 🕒 **Letzte Korrektur nachvollziehbar** - der Sensor zeigt `last_correction`, `offset`, `obis_code`, `raw_sensor`, sowie optional `meter_id` und `tariff_price`
- 🛠️ **HA-Service** - `set_energy_meter` für Automatisierungen, Richtung wird automatisch aus dem Eintrag bestimmt
- 🌍 **Mehrsprachig** - Englische und deutsche Übersetzungen enthalten
- **🧪 Umfangreiche Testabdeckung**
  - Unit-Tests für **Config Flow, Options Flow, Coordinator, Init, Sensor, Migration**
  - CI-Tests für **Python 3.11 und 3.12**

## Voraussetzungen

- Home Assistant **2024.1+**
- Mindestens ein bestehender totaler/kumulativer Energiesensor mit numerischem Zustand
  - z. B. aus einer Smart-Meter-Integration, einem Solarwechselrichter oder MQTT-Sensor

enerABot funktioniert mit **jedem** totalen/kumulativen Netzsensor - unabhängig
von Hersteller oder Integration. Ein Beispiel ist
[huABus](https://github.com/arboeh/huABus), das für Huawei-Solarwechselrichter
`sensor.huawei_solar_inverter_grid_energy_exported` und
`sensor.huawei_solar_inverter_grid_energy_imported` bereitstellt - aber jeder
andere totaler Bezugs-/Einspeisesensor funktioniert genauso gut.

## Funktionsweise

1. Du führst einen Zähler-Eintrag über den Config Flow durch und wählst einen Quellsensor sowie dessen OBIS-Code
2. enerABot bestimmt die Richtung (Bezug/Einspeisung) aus dem OBIS-Code-Präfix (`1.8.x` = Bezug, `2.8.x` = Einspeisung)
3. enerABot erstellt für diesen Eintrag einen gespiegelten Sensor, der den Quellwert mit einem gespeicherten Offset kombiniert
4. Beim Ablesen deines physischen Zählers öffnest du die **Optionen** der Integration und gibst den realen Zählerstand ein
5. enerABot berechnet `offset = realer_zählerstand - aktueller_sensorwert` und speichert ihn
6. Ab sofort meldet der enerABot-Sensor `quellwert + offset` - stets passend zum physischen Zähler
7. Wenn du sowohl einen Bezugs- als auch einen Einspeisesensor hast, fügst du enerABot ein zweites Mal für die andere Richtung hinzu - jedes Zählerregister erhält seinen eigenen Eintrag
8. Optional kannst du den Eintrag mit einer Zähler-ID, einem Tarifpreis und einem Ablesezyklus versehen - entweder direkt bei der Einrichtung oder später über die Optionen. Diese Felder sind rein beschreibende Metadaten und beeinflussen die Offset-Berechnung nicht

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
3. Quellsensor und passenden OBIS-Code auswählen (z. B. `1.8.2` für Bezug, `2.8.2` für Einspeisung)
4. Dem Zähler einen Namen geben und optional den initialen Zählerstand, Zähler-ID, Tarifpreis und Ablesezyklus angeben
5. Der Eintrag wird validiert und automatisch hinzugefügt
6. Den Vorgang ein zweites Mal wiederholen, falls du auch die jeweils andere Richtung (Bezug oder Einspeisung) erfassen möchtest

> Alle Metadatenfelder (Zähler-ID, Tarifpreis, Ablesezyklus) sind optional und können später über die **Optionen** ergänzt oder geändert werden.

## Verwendung

Nach der Einrichtung öffnest du über **Konfigurieren** die Optionen, um Offsets und Metadaten zu korrigieren:

| Option                       | Beschreibung                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| 🔢 Zählerstand korrigieren     | Realen Zählerstand eingeben und optional Zähler-ID, Tarifpreis und Ablesezyklus aktualisieren      |

## Entitäten

Jeder enerABot-Eintrag erstellt genau einen Sensor:

| Entität               | Typ    | Beschreibung                                                    |
| ----------------------- | ------ | ----------------------------------------------------------------- |
| `sensor.<name>`        | Sensor | Energiewert mit angewendetem Offset; benannt "Import" oder "Export" je nach OBIS-Code |

Der Sensor zeigt folgende Attribute:

| Attribut                  | Beschreibung                                                  |
| --------------------------- | ---------------------------------------------------------- |
| `offset`                  | Aktuell gespeicherter Offset-Wert                            |
| `last_correction`         | Zeitstempel der letzten Zählerstand-Korrektur                 |
| `raw_sensor`              | Entity-ID des zugrunde liegenden Quellsensors                 |
| `obis_code`               | OBIS-Code des Registers (z. B. `1.8.2`)                        |
| `meter_id` (optional)     | Seriennummer/Kennung des physischen Zählers, falls konfiguriert |
| `tariff_price` (optional) | Gespeicherter EUR/kWh-Preis, falls konfiguriert                |

## Services

### `enerabot.set_energy_meter`

```yaml
service: enerabot.set_energy_meter
data:
  entity_id: sensor.mein_zaehler
  meter_value: 1234.5
```

Die Richtung (Bezug/Einspeisung) wird automatisch aus dem im passenden Config-Eintrag gespeicherten OBIS-Code bestimmt - eine separate Angabe ist nicht nötig.

## Bekannte Einschränkungen (0.2.0-beta)

- Jeder Eintrag erfasst genau ein Zählerregister - Bezug und Einspeisung erfordern zwei separate Einträge
- Keine Offset-Historie; nur der aktuellste Offset und Korrekturzeitpunkt werden gespeichert
- Noch keine automatische Kostenberechnung aus `tariff_price` (bisher nur Metadaten)
- Nutzer, die von 0.1.x aktualisieren, erhalten eine automatische Migration - ein kombinierter Bezugs+Einspeise-Eintrag wird in zwei separate Einträge aufgeteilt; bitte nach dem Update die Offsets prüfen

## Geplante Funktionen (zukünftige Releases)

- 💶 **Automatische Kostenberechnung** anhand des gespeicherten `tariff_price`
- 📊 **Offset-Historie** - alle vergangenen Korrekturen nachvollziehbar machen, nicht nur die letzte
- 📱 **Lovelace-Karte** für schnelle Zählerkorrektur ohne Öffnen der Optionen
- 🔔 **Abweichungs-Benachrichtigungen** bei Überschreiten eines konfigurierbaren Schwellenwerts
- 🔄 **Generalisierte Sensor-Unterstützung** - beliebige `total_increasing`-Sensoren mit wählbarer Einheit, nicht nur Energie

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Lizenz

MIT © 2026 [arboeh](https://github.com/arboeh) - siehe [LICENSE](LICENSE)
