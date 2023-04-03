CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device TEXT UNIQUE,
    data INTEGER NOT NULL,
    contract INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    revenue NUMERIC NOT NULL,
    commission NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    new BOOLEAN,
    upgrade BOOLEAN,
    device TEXT,
    data INTEGER NOT NULL,
    contract INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    commission NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS targets(
    username TEXT,
    new INTEGER,
    upgrades INTEGER,
    unlimited INTEGER,
    revenue NUMERIC
);

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname NOT NULL,
    pass NOT NULL
);