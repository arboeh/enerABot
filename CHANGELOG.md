# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Sensor-Auswahl bei Einrichtung/Konfiguration auf passende Device
  Classes beschränkt (energy für Energiezähler, monetary für Preis-Sensor),
  um Fehlkonfigurationen zu vermeiden.
- Options dialog field order now matches the alphabetical entity display
  order on the device page (cost reset cycle, price mode, tariff price).

### Fixed
- Missing German/English translation for the `price_sensor` field in the
  initial config flow step (previously only translated in the options flow).
- Englische Übersetzungsdateien (strings.json, translations/en.json,
  services.yaml) enthielten fälschlicherweise den deutschen Begriff
  'Zählerstand' statt 'meter reading'. Jetzt konsistent auf Englisch.

### Added
- `number` platform with `EnerABotTariffPriceNumber` (editable tariff price)
  and `EnerABotOffsetNumber` (editable offset, disabled by default).
- `select` platform with `EnerABotPriceModeSelect` (none / fixed / dynamic)
  and `EnerABotCostResetCycleSelect` (none / monthly / yearly).
- Regression tests for missing config flow translation keys.
