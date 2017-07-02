DROP TABLE IF EXISTS logFile;
CREATE TABLE logFile (
  id INTEGER primary key autoincrement,
  incident INTEGER not null,
  userName TEXT not null,
  realServer TEXT not null,
  timeStamp DATETIME DEFAULT CURRENT_TIMESTAMP not null
);
