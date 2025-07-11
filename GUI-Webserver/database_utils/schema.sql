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
  purity_downstream FLOAT NOT NULL,
  purity_upstream FLOAT NOT NULL,
  ait501_ai FLOAT NOT NULL,
  ti501_ai FLOAT NOT NULL,
  ti502_ai FLOAT NOT NULL,
  ti503_ai FLOAT NOT NULL,
  ti504_ai FLOAT NOT NULL,
  ti505_ai FLOAT NOT NULL,
  ti523_ai FLOAT NOT NULL,

  "Timestamp" TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Pressures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Root_Exhaust_Pressure FLOAT NOT NULL,
  Buffer_Pressure FLOAT NOT NULL,
  Magnet_Pressure FLOAT NOT NULL,
  Purifier_Inlet_Pressure FLOAT NOT NULL,
  Fridge_Vapor_Pressure FLOAT NOT NULL,
  "Timestamp" TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Flow_Rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Seperator_Flow FLOAT NOT NULL,
  Magnet_Flow FLOAT NOT NULL,
  Main_Flow FLOAT NOT NULL,
  "Timestamp" TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime'))
);
