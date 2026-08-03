# custom_components/enerabot/const.py

"""Constants for the enerABot integration."""

DOMAIN = "enerabot"

CONF_NAME = "name"
CONF_IMPORT_SENSOR = "import_sensor"
CONF_EXPORT_SENSOR = "export_sensor"

OPTION_OFFSET_IMPORT = "offset_import"
OPTION_OFFSET_EXPORT = "offset_export"
OPTION_LAST_CORRECTION_IMPORT = "last_correction_import"
OPTION_LAST_CORRECTION_EXPORT = "last_correction_export"

CONF_METER_ID_IMPORT = "meter_id_import"
CONF_METER_ID_EXPORT = "meter_id_export"
CONF_OBIS_CODE_IMPORT = "obis_code_import"
CONF_OBIS_CODE_EXPORT = "obis_code_export"
CONF_READING_CYCLE = "reading_cycle"
CONF_TARIFF_PRICE_IMPORT = "tariff_price_import"
CONF_TARIFF_PRICE_EXPORT = "tariff_price_export"

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

UPDATE_INTERVAL = 30
