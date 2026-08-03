![Logo](images/heading.svg)

🇬🇧 **English** | [🇩🇪 Deutsch](README.de.md)

## Energy Meter Offset Robot for Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![release](https://img.shields.io/github/v/release/arboeh/enerABot?display_name=tag)](https://github.com/arboeh/enerABot/releases/latest)
[![codecov](https://codecov.io/gh/arboeh/enerABot/branch/main/graph/badge.svg)](https://codecov.io/gh/arboeh/enerABot)
[![CI](https://github.com/arboeh/enerABot/workflows/CI/badge.svg)](https://github.com/arboeh/enerABot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/enerABot/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/enerABot/graphs/commit-activity)

> **⚠️ Beta Release** - enerABot 0.2.0-beta is functional but under active development.
> Expect breaking changes before 1.0.0. Please report issues on GitHub.

**enerABot** brings your physical energy meter reading into Home Assistant
electronically - no more manual meter reading. It takes an existing total
(cumulative) grid sensor and lets you align it to the real meter reading
once, via the UI, so the displayed value always matches what's on the
physical meter.

Each enerABot entry represents **one physical meter register** - you select
the source sensor and the corresponding OBIS code (e.g. `1.8.2` for import,
`2.8.2` for export), and enerABot automatically determines whether it's an
import or export meter from that code. If you have both a grid import and a
grid export sensor, simply add enerABot twice - once per direction.

## Features

- 🔢 **Offset calculation** - enter the real meter reading, enerABot calculates and stores the offset automatically
- 🧾 **OBIS code determines direction** - select an OBIS code (e.g. `1.8.2`, `2.8.2`) and enerABot automatically knows whether it's import or export, per IEC 62056-6-1
- 🔌 **Source-agnostic** - works with any total/cumulative energy sensor
- 🆔 **Meter ID tracking** - optionally store the physical meter's serial number/ID
- 💶 **Tariff price (optional)** - store a EUR/kWh price for future cost calculations
- 🗓️ **Reading cycle** - optionally mark a meter as daily, monthly, or manual reading cadence
- 🧮 **Coordinator-based updates** - offsets are applied live on every sensor update
- 🛡️ **Graceful degradation** - unavailable/unknown source sensors don't break statistics (`TOTAL_INCREASING` stays intact)
- 🕒 **Last correction tracking** - the sensor exposes `last_correction`, `offset`, `obis_code`, `raw_sensor`, and optionally `meter_id` and `tariff_price`
- 🛠️ **HA Service** - `set_energy_meter` for automations, direction determined automatically from the entry
- 🌍 **Multi-language** - English and German translations included
- **🧪 Extensive Test Coverage**
  - Unit tests for **config flow, options flow, coordinator, init, sensor, migration**
  - CI tests for **Python 3.11 and 3.12**

## Requirements

- Home Assistant **2024.1+**
- At least one existing total/cumulative energy sensor with a numeric state
  - e.g. from a smart meter integration, solar inverter, or MQTT sensor

enerABot works with **any** total/cumulative grid sensor - it is not tied to
a specific brand or integration. One example source is
[huABus](https://github.com/arboeh/huABus), which exposes
`sensor.huawei_solar_inverter_grid_energy_exported` and
`sensor.huawei_solar_inverter_grid_energy_imported` for Huawei solar
inverters - but any other total import/export energy sensor works just as
well.

## How It Works

1. You add a meter entry via the config flow, selecting one source sensor and its OBIS code
2. enerABot determines the direction (import/export) from the OBIS code prefix (`1.8.x` = import, `2.8.x` = export)
3. enerABot creates one mirrored sensor for that entry, combining the source value with a stored offset
4. When you look at your physical meter, open the integration's **Options** and enter the real reading
5. enerABot calculates `offset = real_reading - current_sensor_value` and stores it
6. From then on, the enerABot sensor reports `source_value + offset` - always matching the physical meter
7. If you have both an import and an export sensor, add enerABot a second time for the other direction - each meter register gets its own entry
8. Optionally, you can tag the entry with a meter ID, tariff price, and reading cycle - either at setup or later via Options. These fields are purely descriptive metadata and don't affect the offset calculation

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
3. Select your source sensor and the matching OBIS code (e.g. `1.8.2` for import, `2.8.2` for export)
4. Give the meter a name, and optionally provide the initial meter reading, meter ID, tariff price, and reading cycle
5. The entry is validated and added automatically
6. Repeat the process a second time if you also want to track the opposite direction (import or export)

> All metadata fields (meter ID, tariff price, reading cycle) are optional and can be added or edited later via **Options**.

## Usage

After setup, open the integration options via **Configure** to correct offsets and update metadata:

| Option                   | Description                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| 🔢 Correct Meter Reading | Enter the real meter reading and optionally update meter ID, tariff price, and reading cycle      |

## Entities

Each enerABot entry creates exactly one sensor:

| Entity                 | Type   | Description                                        |
| ----------------------- | ------ | --------------------------------------------------- |
| `sensor.<name>`         | Sensor | Energy value with offset applied; named "Import" or "Export" based on the OBIS code |

The sensor exposes the following attributes:

| Attribute               | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `offset`                | Currently stored offset value                                |
| `last_correction`       | Timestamp of the last meter reading correction                |
| `raw_sensor`            | Entity ID of the underlying source sensor                     |
| `obis_code`             | OBIS code of the register (e.g. `1.8.2`)                       |
| `meter_id` (optional)   | Physical meter serial number/ID, if configured                |
| `tariff_price` (optional) | Stored EUR/kWh price, if configured                        |

## Services

### `enerabot.set_energy_meter`

```yaml
service: enerabot.set_energy_meter
data:
  entity_id: sensor.my_meter
  meter_value: 1234.5
```

The direction (import/export) is determined automatically from the OBIS code stored in the matching config entry - no need to specify it separately.

## Known Limitations (0.2.0-beta)

- Each entry tracks exactly one meter register - import and export require two separate entries
- No historical offset log; only the most recent offset and correction timestamp are stored
- No automatic cost calculation from `tariff_price` yet (metadata only)
- Users upgrading from 0.1.x will have their existing entries automatically migrated - a combined import+export entry is split into two separate entries; please verify offsets after upgrading

## Planned Features (future releases)

- 💶 **Automatic cost calculation** using the stored `tariff_price`
- 📊 **Offset history** - track all past corrections, not just the latest one
- 📱 **Lovelace card** for quick meter correction without opening options
- 🔔 **Drift notifications** when the calculated offset exceeds a configurable threshold
- 🔄 **Generalized sensor support** - accept any `total_increasing` sensor with selectable unit of measurement, not limited to energy

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT © 2026 [arboeh](https://github.com/arboeh) - see [LICENSE](LICENSE)
