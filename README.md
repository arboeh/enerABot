# enerABot

Home Assistant custom integration for managing energy meter offsets (Import 1.8.0 / Export 2.8.0).

## Overview

enerABot allows you to correct the reading of your energy meter by defining an offset for import and export sensors. It reads the current sensor state, applies the offset, and reports the corrected value. The offset is calculated as `meter_value - current_state` and can be updated via the options flow or services.

## Features

- Entity-based configuration (no IP addresses needed)
- Offset correction for import (1.8.0) and export (2.8.0) energy meters
- Event-driven sensor updates via state change tracking
- Services `set_energy_meter_import` and `set_energy_meter_export` for script-based offset updates
- German and English UI translations

## Installation

1. Copy the `custom_components/enerabot` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → Search for "enerABot"
4. Select your import and export energy sensors

## Configuration

After adding the integration, you can configure the offset correction for each sensor in the integration options. The offset is calculated as:

```
offset = meter_value - current_sensor_state
```

## Services

### `set_energy_meter_import`

Set the import energy meter value and calculate the offset.

| Field | Description | Required |
|-------|-------------|----------|
| `entity_id` | Import energy sensor entity_id | Yes |
| `meter_value` | Current real Zählerstand Bezug (1.8.0) in kWh | Yes |

### `set_energy_meter_export`

Set the export energy meter value and calculate the offset.

| Field | Description | Required |
|-------|-------------|----------|
| `entity_id` | Export energy sensor entity_id | Yes |
| `meter_value` | Current real Zählerstand Einspeisung (2.8.0) in kWh | Yes |

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Linting and Formatting

```bash
ruff check custom_components/ tests/
ruff format custom_components/ tests/
```

### Type Checking

```bash
mypy custom_components/
```

## License

MIT