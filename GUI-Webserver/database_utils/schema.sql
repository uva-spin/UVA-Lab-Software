-- Modified schema to preserve existing data
-- Use CREATE TABLE IF NOT EXISTS instead of DROP TABLE

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
  Pressure_1 FLOAT NOT NULL,
  Pressure_2 FLOAT NOT NULL,
  Pressure_3 FLOAT NOT NULL,
  "Timestamp" TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Flow_Rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Flow_1 FLOAT NOT NULL,
  Flow_2 FLOAT NOT NULL,
  Flow_3 FLOAT NOT NULL,
  "Timestamp" TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime'))
);
