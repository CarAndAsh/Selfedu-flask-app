CREATE TABLE IF NOT EXISTS navigation
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    url  VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS posts
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    post  VARCHAR NOT NULL,
    time INTEGER NOTE NULL
);
