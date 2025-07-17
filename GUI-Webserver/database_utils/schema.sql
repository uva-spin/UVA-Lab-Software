CREATE TABLE IF NOT EXISTS HMI (
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

CREATE TABLE IF NOT EXISTS Pressures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  root_exhaust_pressure FLOAT,
  buffer_pressure FLOAT,
  magnet_pressure FLOAT,
  purifier_inlet_pressure FLOAT,
  fridge_vapor_pressure FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Flow_Rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seperator_flow FLOAT,
  magnet_flow FLOAT,
  main_flow FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Lakeshore_Target_Stick (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  buffle_top_temperature FLOAT,
  buffle_bottom_temperature FLOAT,
  seperator_top_temperature FLOAT,
  seperator_bottom_temperature FLOAT,
  heat_exchanger_top_temperature FLOAT,
  heat_exchanger_bottom_temperature FLOAT,
  annealing_plate_bar_temperature FLOAT,
  annealing_plate_top_temperature FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Lakeshore_Fridge_Temp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_top_up_temperature FLOAT,
  target_top_up_center_temperature FLOAT,
  target_top_down_temperature FLOAT,
  target_bottom_up_temperature FLOAT, 
  target_bottom_up_center_temperature FLOAT,
  target_bottom_down_temperature FLOAT,
  target_top_cernox_temperature FLOAT,
  target_bottom_cernox_temperature FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);


CREATE TABLE IF NOT EXISTS MaxiGauge (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  maxigauge_seperator_inlet_pressure FLOAT,
  maxigauge_upper_roots_pressure FLOAT,
  channel_3 FLOAT,
  channel_4 FLOAT,
  channel_5 FLOAT,
  channel_6 FLOAT,
  "Timestamp" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);