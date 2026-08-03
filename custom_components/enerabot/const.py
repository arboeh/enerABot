# custom_components/enerabot/const.py

"""Constants for the enerABot integration."""

DOMAIN = "enerabot"

CONF_NAME = "name"
CONF_SENSOR = "sensor"
CONF_METER_ID = "meter_id"
CONF_OBIS_CODE = "obis_code"
CONF_TARIFF_PRICE = "tariff_price"
CONF_READING_CYCLE = "reading_cycle"

OPTION_OFFSET = "offset"
OPTION_LAST_CORRECTION = "last_correction"

READING_CYCLE_DAILY = "daily"
READING_CYCLE_MONTHLY = "monthly"
READING_CYCLE_MANUAL = "manual"
READING_CYCLE_OPTIONS = [READING_CYCLE_DAILY, READING_CYCLE_MONTHLY, READING_CYCLE_MANUAL]

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
