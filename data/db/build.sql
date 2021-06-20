CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "a!"
);

CREATE TABLE IF NOT EXISTS members (
	UserID integer PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS exp (
	GuildID integer,
	UserID integer,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(GuildID, UserID)
);

CREATE TABLE IF NOT EXISTS bank (
	GuildID integer,
	UserID integer,
	Wallet integer DEFAULT 0,
	Bank integer DEFAULT 0,
	WorkLock text DEFAULT CURRENT_TIMESTAMP,
	DailyLock text DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(GuildID, UserID)
);