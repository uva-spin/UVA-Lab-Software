CREATE TABLE IF NOT EXISTS QT (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  fc501_ai FLOAT NOT NULL,
  fc501_out FLOAT NOT NULL,
  fc502_ai FLOAT NOT NULL,
  fc502_out FLOAT NOT NULL,
  lit501_ai FLOAT NOT NULL, 
  pt501_ai FLOAT NOT NULL,
  pt502_ai FLOAT NOT NULL,
  pt503_ai FLOAT NOT NULL,
  pt504_ai FLOAT NOT NULL,
  ait501_ai FLOAT NOT NULL,
  ti501_ai FLOAT NOT NULL,
  ti502_ai FLOAT NOT NULL,
  ti503_ai FLOAT NOT NULL,
  ti504_ai FLOAT NOT NULL,
  ti505_ai FLOAT NOT NULL,
  ti523_ai FLOAT NOT NULL,

  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Labjack (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  root_exhaust_pressure FLOAT,
  buffer_pressure FLOAT,
  magnet_pressure FLOAT,
  purifier_inlet_pressure FLOAT,
  fridge_vapor_pressure FLOAT,
  thermocouple FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Flow_Rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seperator_flow FLOAT,
  magnet_flow FLOAT,
  main_flow FLOAT,
  microwave_flow_meter FLOAT,
  heat_exchanger_flow_meter FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Lakeshore_Target_Stick (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_stick_buffle_top_temperature FLOAT,
  target_stick_buffle_bottom_temperature FLOAT,
  target_stick_seperator_top_temperature FLOAT,
  target_stick_seperator_bottom_temperature FLOAT,
  target_stick_heat_exchanger_top_temperature FLOAT,
  target_stick_heat_exchanger_bottom_temperature FLOAT,
  target_stick_annealing_plate_bar_temperature FLOAT,
  target_stick_annealing_plate_top_temperature FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Lakeshore_Fridge_Temp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fridge_target_top_up_temperature FLOAT,
  fridge_target_top_up_center_temperature FLOAT,
  fridge_target_top_down_temperature FLOAT,
  fridge_target_bottom_up_temperature FLOAT, 
  fridge_target_bottom_up_center_temperature FLOAT,
  fridge_target_bottom_down_temperature FLOAT,
  fridge_target_top_cernox_temperature FLOAT,
  fridge_target_bottom_cernox_temperature FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Lakeshore_Magnet_Temp (
  id Integer PRIMARY KEY AUTOINCREMENT,
  magnet_channel_1 FLOAT,
  magnet_channel_2 FLOAT,
  magnet_channel_3 FLOAT,
  magnet_channel_4 FLOAT,
  magnet_channel_5 FLOAT,
  magnet_channel_6 FLOAT,
  magnet_channel_7 FLOAT,
  magnet_channel_8 FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS MaxiGauge (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  maxigauge_seperator_inlet_pressure FLOAT,
  maxigauge_upper_roots_pressure FLOAT,
  maxigauge_channel_3 FLOAT,
  maxigauge_channel_4 FLOAT,
  maxigauge_channel_5 FLOAT,
  maxigauge_channel_6 FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS IVC (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ivc_pressure FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS NMR (
id INTEGER PRIMARY KEY AUTOINCREMENT,
run_number INTEGER,
measurement_type TEXT,
peak_amp FLOAT,
peak_center FLOAT,
beam_on INTEGER,
rf_level FLOAT,
if_atten FLOAT,
he_temperature FLOAT,
he_pressure FLOAT,
nmr_channel INTEGER,
temperature FLOAT,
calibration_constant FLOAT,
polarization FLOAT,
polarization_std FLOAT,
snr FLOAT,
step_width FLOAT,
center_freq FLOAT,
freq_span FLOAT,
area FLOAT,
phase_voltage FLOAT,
tune_voltage FLOAT
"Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

PRAGMA journal_mode = WAL;