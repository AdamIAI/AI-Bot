CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "a!"
);

CREATE TABLE IF NOT EXISTS members (
	UserID integer PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS exp (
	GuildID integer PRIMARY KEY,
	UserID integer,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (UserID) REFERENCES members(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bank (
	GuildID integer PRIMARY KEY,
	UserID integer,
	Wallet integer DEFAULT 0,
	Bank integer DEFAULT 0,
	WorkLock text DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (UserID) REFERENCES members(UserID) ON DELETE CASCADE
);