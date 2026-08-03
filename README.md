![Logo](images/heading.svg)

🇬🇧 **English** | [🇩🇪 Deutsch](README.de.md)

## Energy Meter Offset Manager for Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![release](https://img.shields.io/github/v/release/arboeh/enerABot?display_name=tag)](https://github.com/arboeh/enerABot/releases/latest)
[![codecov](https://codecov.io/gh/arboeh/enerABot/branch/main/graph/badge.svg)](https://codecov.io/gh/arboeh/enerABot)
[![CI](https://github.com/arboeh/enerABot/workflows/CI/badge.svg)](https://github.com/arboeh/enerABot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/enerABot/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/enerABot/graphs/commit-activity)

> **⚠️ Beta Release** - enerABot 0.1.0-beta is functional but under active development.
> Expect breaking changes before 1.0.0. Please report issues on GitHub.

**enerABot** brings your physical energy meter reading into Home Assistant
electronically - no more manual meter reading. It takes your existing total
(cumulative) grid import and/or export sensors and lets you align them to the
real meter reading once, via the UI, so the displayed value always matches
what's on the physical meter.

This is useful whenever a sensor's cumulative counter doesn't match the
physical meter - e.g. after replacing an inverter, migrating an integration,
a sensor reset, or simply because the source integration started counting
from zero instead of the meter's actual reading.

enerABot works with **any** total/cumulative grid sensor - it is not tied to
a specific brand or integration. One example source is
[huABus](https://github.com/arboeh/huABus), which exposes
`sensor.huawei_solar_inverter_grid_energy_exported` and
`sensor.huawei_solar_inverter_grid_energy_imported` for Huawei solar
inverters - but any other total import/export energy sensor works just as
well.

## Features

- 🔢 **Offset calculation** - enter the real meter reading, enerABot calculates and stores the offset automatically
- ⚡ **Import and/or export** - configure only an import sensor, only an export sensor, or both - whichever your setup provides
- 🔌 **Source-agnostic** - works with any total/cumulative energy sensor (single-direction or bidirectional meters)
- 🧮 **Coordinator-based updates** - offsets are applied live on every sensor update
- 🛡️ **Graceful degradation** - unavailable/unknown source sensors don't break statistics (`TOTAL_INCREASING` stays intact)
- 🕒 **Last correction tracking** - each sensor exposes `last_correction` and `offset` as attributes
- 🛠️ **HA Services** - `set_energy_meter_import`, `set_energy_meter_export` for automations
- 🌍 **Multi-language** - English and German translations included
- **🧪 Extensive Test Coverage**
  - Unit tests for **config flow, options flow, coordinator, init, sensors**
  - CI tests for **Python 3.11 and 3.12**

## Requirements

- Home Assistant **2024.1+**
- At least one existing total/cumulative energy sensor (import and/or
  export) with numeric state - e.g. from a smart meter integration, solar
  inverter, or MQTT sensor. Both sensors are optional individually, but at
  least one must be configured.

## How It Works

1. You add a meter pair via the config flow, configuring an import sensor,
   an export sensor, or both
2. enerABot creates a matching sensor for each configured direction, mirroring
   the source sensor plus a stored offset
3. When you look at your physical meter, open the integration's **Options**
   and enter the real reading for import or export
4. enerABot calculates `offset = real_reading - current_sensor_value` and stores it
5. From then on, the enerABot sensor reports `source_value + offset` - always
   matching the physical meter without you having to read it again

## Installation via HACS

1. Open HACS → **Integrations**
2. Click **⋮ → Custom repositories**
3. Add `https://github.com/arboeh/enerABot` as type **Integration**
4. Search for **enerABot** and install
5. Restart Home Assistant

## Manual Installation

1. Copy `custom_components/enerabot/` to your `config/custom_components/` folder
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **enerABot**
3. Select your import sensor, export sensor, or both, and give the meter pair a name
4. The pair is validated and added automatically

## Usage

After setup, open the integration options via **Configure** to correct offsets:

| Option                   | Description                                               |
| ------------------------ | ----------------------------------------------------------|
| 🔢 Correct Import Meter  | Enter the real meter reading for Bezug (1.8.0)             |
| 🔢 Correct Export Meter  | Enter the real meter reading for Einspeisung (2.8.0)        |

## Entities

For each configured direction, enerABot creates:

| Entity                            | Type   | Description                                  |
| --------------------------------- | ------ | --------------------------------------------- |
| `sensor.<name>_import`            | Sensor | Import energy value with offset applied       |
| `sensor.<name>_export`            | Sensor | Export energy value with offset applied       |

Both sensors expose `offset`, `last_correction` and `raw_sensor` as attributes.

## Services

### `enerabot.set_energy_meter_import`

```yaml
service: enerabot.set_energy_meter_import
data:
  entity_id: sensor.my_import
  meter_value: 1234.5
```

### `enerabot.set_energy_meter_export`

```yaml
service: enerabot.set_energy_meter_export
data:
  entity_id: sensor.my_export
  meter_value: 567.8
```

## Known Limitations (0.1.0-beta)

- Only one import and one export sensor per meter pair
- No historical offset log; only the most recent offset and correction timestamp are stored

## Planned Features (future releases)

- 📊 **Offset history**
  Track all past corrections, not just the latest one
- 📱 **Lovelace card**
  Dedicated card for quick meter correction without opening options
- 🔔 **Drift notifications**
  Alert when the calculated offset exceeds a configurable threshold

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT © 2026 [arboeh](https://github.com/arboeh) - see [LICENSE](LICENSE)