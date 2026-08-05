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
  - 💶 **Dynamische Preisunterstützung** - fester EUR/kWh-Preis oder Verknüpfung mit einem dynamischen Preissensor (z. B. Tibber, Nord Pool, Awattar)
  - 🧮 **Automatische Kostenberechnung** - ein eigener Kosten-Sensor akkumuliert die Kosten inkrementell auf Basis der konfigurierten Preisquelle
  - 🔄 **Kosten-Reset-Zyklus** - akkumulierte Kosten automatisch monatlich, jährlich oder nie zurücksetzen lassen
  - 🔘 **Reset-Button und -Service** - Offset und Kosten für einen oder alle Zähler per UI-Button oder `enerabot.reset_meter`-Service zurücksetzen
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

## Preisquellen und Kostenerfassung

Jeder enerABot-Eintrag kann optional zusätzlich zur Energie auch Kosten erfassen:

1. Wähle bei der Einrichtung oder später über die Optionen einen **Preismodus**: `Kein Preis`, `Fester Preis` oder `Dynamischer Preissensor`
2. Bei **Fester Preis** gibst du direkt einen EUR/kWh-Wert ein
3. Bei **Dynamischer Preissensor** wählst du eine beliebige Sensor-Entity, die den aktuellen Preis liefert (z. B. aus einer Tibber-, Nord-Pool- oder Awattar-Integration, oder eines eigenen Template-Sensors)
4. Ist eine Preisquelle konfiguriert, erstellt enerABot einen zusätzlichen **Kosten**-Sensor, der die Kosten inkrementell akkumuliert - nur der seit dem letzten Update verbrauchte Energiedelta wird mit dem zu diesem Zeitpunkt gültigen Preis verrechnet, sodass vergangene Kosten auch bei späteren Preisänderungen korrekt bleiben
5. Wähle einen **Kosten-Reset-Zyklus**: `Nie` (laufender Gesamtwert seit Einrichtung), `Monatlich` oder `Jährlich` - der Kosten-Sensor setzt sich zu Beginn der nächsten Periode automatisch auf 0 zurück

> Eine spätere Änderung der Preisquelle berechnet vergangene Kosten nicht neu - nur zukünftige Energie-Deltas nutzen den neuen Preis.

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

- **Preis-Sensor**: Nur erforderlich, wenn Preis-Modus auf "Dynamischer Preis" gesetzt ist. Wähle eine beliebige Sensor-Entity, die den aktuellen Preis pro kWh liefert (z. B. aus einer Tibber-, Nord-Pool- oder Awattar-Integration, oder eines eigenen Template-Sensors).

> Alle Metadatenfelder (Zähler-ID, Tarifpreis, Ablesezyklus) sind optional und können später über die **Optionen** ergänzt oder geändert werden.

## Verwendung

Nach der Einrichtung öffnest du über **Konfigurieren** die Optionen, um Offsets und Metadaten zu korrigieren:

| Option                       | Beschreibung                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| 🔢 Zählerstand korrigieren     | Realen Zählerstand eingeben und optional Zähler-ID, Tarifpreis und Ablesezyklus aktualisieren      |

## Entitäten

Für jeden konfigurierten Zähler erstellt enerABot folgende Entitäten:

| Entität                             | Typ    | Beschreibung                                   |
| -------------------------------------- | ------ | ------------------------------------------------|
| `sensor.<name>`                       | Sensor | Energiewert mit angewendetem Offset; benannt "Import" oder "Export" je nach OBIS-Code |
| `sensor.<name>_cost` (optional)       | Sensor | Akkumulierte Kosten, nur falls eine Preisquelle konfiguriert ist |
| `button.<name>_reset`                 | Button | Setzt Offset, Kosten und Korrekturverlauf für diesen Zähler zurück |
| `number.<name>_tariff_price`      | Number | Editierbarer Tarifpreis (EUR/kWh), erscheint als Konfigurations-Entität auf der Geräteseite |
| `number.<name>_offset`            | Number (standardmäßig deaktiviert) | Editierbarer Offset, erscheint als Konfigurations-Entität auf der Geräteseite |
| `select.<name>_price_mode`        | Select | Editierbarer Preis-Modus (keine / fest / dynamisch), erscheint als Konfigurations-Entität |
| `select.<name>_cost_reset_cycle`  | Select | Editierbarer Kosten-Reset-Zyklus (nie / monatlich / jährlich), erscheint als Konfigurations-Entität |

## Kosten-Entität (optional)

Ist eine Preisquelle konfiguriert, erstellt enerABot eine zusätzliche Entität pro Zähler:

| Entität                    | Typ    | Beschreibung                                                |
| ---------------------------- | ------ | ----------------------------------------------------------- |
| `sensor.<name>_cost`        | Sensor | Akkumulierte Kosten in deiner Währung, basierend auf der konfigurierten Preisquelle |

Diese Entität ist nicht verfügbar, wenn keine Preisquelle konfiguriert ist, oder wenn der verknüpfte dynamische Preissensor nicht verfügbar ist.

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

### `enerabot.reset_meter`

Setzt den gespeicherten Offset, Kosten-Akkumulator und Korrekturverlauf für einen oder alle konfigurierten Zähler zurück.

```yaml
service: enerabot.reset_meter
data:
  entity_id: sensor.mein_zaehler
```

```yaml
service: enerabot.reset_meter
data:
  reset_all: true
```

> ⚠️ Nach einem Reset zeigt der Zähler-Sensor wieder den unkorrigierten Rohwert des Quellsensors an, bis du über die Optionen einen neuen Zählerstand eingibst.

Alternativ kannst du die **Reset**-Button-Entität jedes Zählers nutzen, um denselben Vorgang direkt über die UI auszulösen, ohne die Entwicklerwerkzeuge zu öffnen.

## Bekannte Einschränkungen (0.3.1)

- Jeder Eintrag erfasst genau ein Zählerregister - Bezug und Einspeisung erfordern zwei separate Einträge
- Keine Offset-Historie; nur der aktuellste Offset und Korrekturzeitpunkt werden gespeichert
- Nutzer, die von 0.1.x aktualisieren, erhalten eine automatische Migration - ein kombinierter Bezugs+Einspeise-Eintrag wird in zwei separate Einträge aufgeteilt; bitte nach dem Update die Offsets prüfen
- Die Kostenberechnung setzt voraus, dass der verknüpfte Preissensor einen Preis pro kWh in derselben Währung wie deine Home-Assistant-Instanz liefert - keine automatische Währungsumrechnung
- Eine nachträgliche Änderung der Preisquelle berechnet vergangene Kosten nicht neu
- Ein Reset löscht die Kostenhistorie eines Zählers vollständig - ein Reset kann nicht rückgängig gemacht werden

## Geplante Funktionen (zukünftige Releases)

- 📊 **Offset- und Kosten-Historie** - alle vergangenen Korrekturen und Kostenperioden nachvollziehbar machen, nicht nur die aktuelle
- 📱 **Lovelace-Karte** für schnelle Zählerkorrektur und Kostenübersicht ohne Öffnen der Optionen
- 🔔 **Abweichungs- und Preis-Benachrichtigungen** - Warnung bei starker Offset-Drift oder ungewöhnlich hohen dynamischen Preisen
- 🔄 **Generalisierte Sensor-Unterstützung** - beliebige `total_increasing`-Sensoren mit wählbarer Einheit, nicht nur Energie

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Lizenz

MIT © 2026 [arboeh](https://github.com/arboeh) - siehe [LICENSE](LICENSE)
