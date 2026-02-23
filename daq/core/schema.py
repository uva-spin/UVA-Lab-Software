"""
Schema definitions: table names and column mappings.
Single source of truth aligned with schema.sql.
Enables type-safe, declarative INSERT generation.
"""
from typing import Dict, List, Tuple

TABLE_SCHEMAS: Dict[str, List[str]] = {
    "QT": [
        "fc501_ai", "fc501_out", "fc502_ai", "fc502_out", "lit501_ai",
        "pt501_ai", "pt502_ai", "pt503_ai", "pt504_ai",
        "ait501_ai", "ti501_ai", "ti502_ai", "ti503_ai", "ti504_ai", "ti505_ai", "ti523_ai",
        "Timestamp",
    ],
    "Flow_Rates": ["seperator_flow", "magnet_flow", "main_flow", "Timestamp"],
    "Flow_Rates_extra": ["microwave_flow", "heat_exchanger_flow", "Timestamp"],
    "Labjack": [
        "root_exhaust_pressure", "buffer_pressure", "magnet_pressure",
        "purifier_inlet_pressure", "fridge_vapor_pressure", "thermocouple",
        "Timestamp",
    ],
    "Labjack_extra": ["magnet_bottom_temperature", "magnet_top_temperature", "Timestamp"],
    "Lakeshore_Target_Stick": [
        "target_stick_buffle_top_temperature", "target_stick_buffle_bottom_temperature",
        "target_stick_seperator_top_temperature", "target_stick_seperator_bottom_temperature",
        "target_stick_heat_exchanger_top_temperature", "target_stick_heat_exchanger_bottom_temperature",
        "target_stick_annealing_plate_bar_temperature", "target_stick_annealing_plate_top_temperature",
        "Timestamp",
    ],
    "Lakeshore_Fridge_Temp": [
        "fridge_target_top_up_temperature", "fridge_target_top_up_center_temperature",
        "fridge_target_top_down_temperature", "fridge_target_bottom_up_temperature",
        "fridge_target_bottom_up_center_temperature", "fridge_target_bottom_down_temperature",
        "fridge_target_top_cernox_temperature", "fridge_target_bottom_cernox_temperature",
        "Timestamp",
    ],
    "Lakeshore_Magnet_Temp": [
        "magnet_channel_1", "magnet_channel_2", "magnet_channel_3", "magnet_channel_4",
        "magnet_channel_5", "magnet_channel_6", "magnet_channel_7", "magnet_channel_8",
        "Timestamp",
    ],
    "MaxiGauge": [
        "maxigauge_seperator_inlet_pressure", "maxigauge_upper_roots_pressure",
        "maxigauge_channel_3", "maxigauge_channel_4", "maxigauge_channel_5", "maxigauge_channel_6",
        "Timestamp",
    ],
    "IVC": ["ivc_pressure", "Timestamp"],
}

# QT raw indices → schema columns (standalone uses 18 values, we map 16 + skip 2)
QT_RAW_TO_COLS = [
    (0, "fc501_ai"), (1, "fc501_out"), (2, "fc502_ai"), (3, "fc502_out"),
    (4, "lit501_ai"), (5, "pt501_ai"), (6, "pt502_ai"), (7, "pt503_ai"), (8, "pt504_ai"),
    (11, "ait501_ai"), (12, "ti501_ai"), (13, "ti502_ai"), (14, "ti503_ai"),
    (15, "ti504_ai"), (16, "ti505_ai"), (17, "ti523_ai"),
]
