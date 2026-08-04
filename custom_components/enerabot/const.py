# custom_components/enerabot/const.py

"""Constants for the enerABot integration."""

from __future__ import annotations

DOMAIN = "enerabot"

PLATFORMS = ["sensor", "button"]

CONF_NAME = "name"
CONF_SENSOR = "sensor"
CONF_METER_ID = "meter_id"
CONF_OBIS_CODE = "obis_code"
CONF_TARIFF_PRICE = "tariff_price"
CONF_PRICE_MODE = "price_mode"
CONF_PRICE_SENSOR = "price_sensor"
CONF_READING_CYCLE = "reading_cycle"
CONF_COST_RESET_CYCLE = "cost_reset_cycle"

OPTION_OFFSET = "offset"
OPTION_LAST_CORRECTION = "last_correction"
OPTION_COST_TOTAL = "cost_total"
OPTION_COST_PERIOD_START = "cost_period_start"
OPTION_COST_LAST_ENERGY = "cost_last_energy"

READING_CYCLE_DAILY = "daily"
READING_CYCLE_MONTHLY = "monthly"
READING_CYCLE_MANUAL = "manual"
READING_CYCLE_OPTIONS = [READING_CYCLE_DAILY, READING_CYCLE_MONTHLY, READING_CYCLE_MANUAL]

PRICE_MODE_NONE = "none"
PRICE_MODE_FIXED = "fixed"
PRICE_MODE_DYNAMIC = "dynamic"
PRICE_MODE_OPTIONS = [PRICE_MODE_NONE, PRICE_MODE_FIXED, PRICE_MODE_DYNAMIC]

COST_RESET_NONE = "none"
COST_RESET_MONTHLY = "monthly"
COST_RESET_YEARLY = "yearly"
COST_RESET_OPTIONS = [COST_RESET_NONE, COST_RESET_MONTHLY, COST_RESET_YEARLY]

OBIS_CODE_OPTIONS = [
    "1.8.0",  # Strombezug Gesamt
    "1.8.1",  # Strombezug HT
    "1.8.2",  # Strombezug NT / Eintarif
    "2.8.0",  # Einspeisung Gesamt
    "2.8.1",  # Einspeisung HT
    "2.8.2",  # Einspeisung NT / Eintarif
]


def is_import_obis(obis_code: str) -> bool:
    """Return True if the OBIS code represents an import register."""
    return obis_code.startswith("1.8")


def is_export_obis(obis_code: str) -> bool:
    """Return True if the OBIS code represents an export register."""
    return obis_code.startswith("2.8")


UPDATE_INTERVAL = 30

SERVICE_RESET_METER = "reset_meter"
ATTR_RESET_ALL = "reset_all"
