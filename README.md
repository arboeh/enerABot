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
  - 💶 **Dynamic price support** - use a fixed EUR/kWh price, or link a dynamic price sensor (e.g. Tibber, Nord Pool, Awattar) instead
  - 🧮 **Automatic cost calculation** - a dedicated cost sensor accumulates cost incrementally based on the configured price source
  - 🔄 **Cost reset cycle** - let accumulated cost reset automatically monthly, yearly, or never
  - 🔘 **Reset button and service** - reset offset and cost for one meter or all meters at once, via UI button or `enerabot.reset_meter` service
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

## Price Sources and Cost Tracking

Each enerABot entry can optionally track cost alongside energy:

1. Choose a **price mode** during setup or later via Options: `None`, `Fixed price`, or `Dynamic price sensor`
2. With **Fixed price**, enter a EUR/kWh value directly
3. With **Dynamic price sensor**, select any sensor entity that reports the current price (e.g. from a Tibber, Nord Pool, or Awattar integration, or your own template sensor)
4. If a price source is configured, enerABot creates an additional **Cost** sensor that accumulates cost incrementally - only the energy consumed since the last update is multiplied by the price valid at that moment, so past cost stays accurate even if the price changes later
5. Choose a **cost reset cycle**: `None` (running total since setup), `Monthly`, or `Yearly` - the cost sensor resets to 0 automatically at the start of the next period

> Changing the price source later does not recalculate past cost - only future energy deltas use the new price.

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

- **Price Sensor**: Only required when Price Mode is set to "Dynamic price". Select any sensor entity that provides the current price per kWh (e.g. from a Tibber, Nord Pool or Awattar integration, or a custom template sensor).

> All metadata fields (meter ID, tariff price, reading cycle) are optional and can be added or edited later via **Options**.

## Usage

After setup, open the integration options via **Configure** to correct offsets and update metadata:

| Option                   | Description                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| 🔢 Correct Meter Reading | Enter the real meter reading and optionally update meter ID, tariff price, and reading cycle      |

## Entities

For each configured meter, enerABot creates the following entities:

| Entity                            | Type   | Description                                  |
| --------------------------------- | ------ | --------------------------------------------- |
| `sensor.<name>`                   | Sensor | Energy value with offset applied; named "Import" or "Export" based on the OBIS code |
| `sensor.<name>_cost` (optional)   | Sensor | Accumulated cost, only if a price source is configured |
| `button.<name>_reset`             | Button | Resets offset, cost, and correction history for this meter |
| `number.<name>_tariff_price`      | Number | Editable tariff price (EUR/kWh), shown as a configuration entity on the device page |
| `number.<name>_offset`            | Number (disabled by default) | Editable offset, shown as a configuration entity on the device page |
| `select.<name>_price_mode`        | Select | Editable price mode (none / fixed / dynamic), shown as a configuration entity |
| `select.<name>_cost_reset_cycle`  | Select | Editable cost reset cycle (none / monthly / yearly), shown as a configuration entity |

## Cost Entity (optional)

If a price source is configured, enerABot creates one additional entity per meter:

| Entity                 | Type   | Description                                                |
| ------------------------ | ------ | ----------------------------------------------------------- |
| `sensor.<name>_cost`    | Sensor | Accumulated cost in your currency, based on the configured price source |

This entity is unavailable if no price source is configured, or if the linked dynamic price sensor becomes unavailable.

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

### `enerabot.reset_meter`

Resets the stored offset, cost accumulator, and correction history for one meter or all configured meters.

```yaml
service: enerabot.reset_meter
data:
  entity_id: sensor.my_meter
```

```yaml
service: enerabot.reset_meter
data:
  reset_all: true
```

> ⚠️ After a reset, the meter sensor reports the raw, uncorrected source value again until you enter a new meter reading via Options.

Alternatively, use the **Reset** button entity created for each meter to trigger the same action from the UI, without needing Developer Tools.

## Known Limitations (0.3.0)

- Each entry tracks exactly one meter register - import and export require two separate entries
- No historical offset log; only the most recent offset and correction timestamp are stored
- Users upgrading from 0.1.x will have their existing entries automatically migrated - a combined import+export entry is split into two separate entries; please verify offsets after upgrading
- Cost calculation assumes the linked price sensor reports a per-kWh price in the same currency as your Home Assistant instance - no automatic currency conversion
- Changing the price source retroactively does not recalculate historical cost
- Resetting a meter clears its cost history entirely - there is no way to undo a reset

## Planned Features (future releases)

- 📊 **Offset and cost history** - track all past corrections and cost periods, not just the current one
- 📱 **Lovelace card** for quick meter correction and cost overview without opening options
- 🔔 **Drift and price notifications** - alert on large offset drift or unusually high dynamic prices
- 🔄 **Generalized sensor support** - accept any `total_increasing` sensor with selectable unit of measurement, not limited to energy

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT © 2026 [arboeh](https://github.com/arboeh) - see [LICENSE](LICENSE)
