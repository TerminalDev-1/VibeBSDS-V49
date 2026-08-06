import os
import secrets
import sqlite3
import threading
import time

from Classes.GameData import (
    BRAWLER_CARD_IDS,
    brawl_pass_credit_reward,
    star_road_remaining,
    trophy_delta,
)


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


class GameDatabase:
    def __init__(self, path=None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = path or os.environ.get("VIBEBSDS_DB", os.path.join(base, "player.sqlite"))
        self._migration_lock = threading.Lock()
        self.migrate()

    def connect(self):
        connection = sqlite3.connect(
            self.path, timeout=15, factory=ClosingConnection
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 15000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def migrate(self):
        with self._migration_lock, self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER NOT NULL
                );
                INSERT INTO schema_version(version)
                SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version);

                CREATE TABLE IF NOT EXISTS accounts (
                    low_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    high_id INTEGER NOT NULL DEFAULT 0,
                    token TEXT NOT NULL UNIQUE,
                    android_id TEXT UNIQUE,
                    name TEXT NOT NULL DEFAULT 'VibePlayer',
                    name_set INTEGER NOT NULL DEFAULT 1,
                    thumbnail INTEGER NOT NULL DEFAULT 0,
                    name_color INTEGER NOT NULL DEFAULT 0,
                    region TEXT NOT NULL DEFAULT 'CA',
                    creator TEXT NOT NULL DEFAULT 'VibeBSDS',
                    coins INTEGER NOT NULL DEFAULT 1000,
                    gems INTEGER NOT NULL DEFAULT 100,
                    star_points INTEGER NOT NULL DEFAULT 0,
                    club_coins INTEGER NOT NULL DEFAULT 0,
                    credits INTEGER NOT NULL DEFAULT 0,
                    chroma_credits INTEGER NOT NULL DEFAULT 0,
                    fame INTEGER NOT NULL DEFAULT 0,
                    trophies INTEGER NOT NULL DEFAULT 5,
                    highest_trophies INTEGER NOT NULL DEFAULT 5,
                    experience INTEGER NOT NULL DEFAULT 0,
                    level INTEGER NOT NULL DEFAULT 1,
                    tokens INTEGER NOT NULL DEFAULT 0,
                    token_doubler INTEGER NOT NULL DEFAULT 0,
                    selected_brawler INTEGER NOT NULL DEFAULT 0,
                    battle_count INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    tutorial_state INTEGER NOT NULL DEFAULT 2,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS brawlers (
                    account_low_id INTEGER NOT NULL,
                    brawler_id INTEGER NOT NULL,
                    card_id INTEGER NOT NULL,
                    trophies INTEGER NOT NULL DEFAULT 5,
                    highest_trophies INTEGER NOT NULL DEFAULT 5,
                    power_level INTEGER NOT NULL DEFAULT 1,
                    power_points INTEGER NOT NULL DEFAULT 0,
                    state INTEGER NOT NULL DEFAULT 2,
                    mastery_points INTEGER NOT NULL DEFAULT 0,
                    mastery_claimed INTEGER NOT NULL DEFAULT 0,
                    unlocked_at INTEGER NOT NULL,
                    PRIMARY KEY (account_low_id, brawler_id),
                    FOREIGN KEY (account_low_id) REFERENCES accounts(low_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS battles (
                    battle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_low_id INTEGER NOT NULL,
                    map_id INTEGER NOT NULL,
                    result INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    brawler_id INTEGER NOT NULL,
                    trophy_delta INTEGER NOT NULL,
                    tokens INTEGER NOT NULL,
                    credits INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (account_low_id) REFERENCES accounts(low_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS progression_actions (
                    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_low_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    subject_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    UNIQUE(account_low_id, action_type, subject_id),
                    FOREIGN KEY (account_low_id) REFERENCES accounts(low_id) ON DELETE CASCADE
                );

                -- The patched V49 client has no safe unset-name onboarding scene.
                UPDATE accounts SET name_set = 1 WHERE name_set = 0;
                -- V49.194's first total-trophy milestone starts at five. Values
                -- below it make the client request milestone index -1 while
                -- constructing the home trophy-road widget.
                UPDATE accounts SET trophies = 5, highest_trophies = MAX(5, highest_trophies)
                WHERE trophies < 5;
                UPDATE brawlers SET trophies = 5, highest_trophies = MAX(5, highest_trophies)
                WHERE trophies < 5;
            """)

    def _load(self, db, low_id):
        account = db.execute("SELECT * FROM accounts WHERE low_id = ?", (low_id,)).fetchone()
        if account is None:
            return None
        brawlers = db.execute(
            "SELECT * FROM brawlers WHERE account_low_id = ? ORDER BY brawler_id", (low_id,)
        ).fetchall()
        return dict(account), [dict(row) for row in brawlers]

    def login(self, account_id, token, android_id=None):
        high_id, low_id = account_id
        with self.connect() as db:
            row = None
            if low_id and token:
                row = db.execute(
                    "SELECT low_id FROM accounts WHERE high_id = ? AND low_id = ? AND token = ?",
                    (high_id, low_id, token),
                ).fetchone()
            if row is None and android_id:
                row = db.execute(
                    "SELECT low_id FROM accounts WHERE android_id = ?", (android_id,)
                ).fetchone()
            if row is None:
                now = int(time.time())
                cursor = db.execute(
                    "INSERT INTO accounts(token, android_id, name, name_set, created_at, updated_at) VALUES (?, ?, 'VibePlayer', 1, ?, ?)",
                    (secrets.token_urlsafe(30), android_id or None, now, now),
                )
                low_id = cursor.lastrowid
                db.execute(
                    "INSERT INTO brawlers(account_low_id, brawler_id, card_id, unlocked_at) VALUES (?, 0, ?, ?)",
                    (low_id, BRAWLER_CARD_IDS[0], now),
                )
            else:
                low_id = row["low_id"]
            return self._load(db, low_id)

    def load(self, low_id):
        with self.connect() as db:
            return self._load(db, low_id)

    def update_name(self, low_id, name):
        with self.connect() as db:
            db.execute(
                "UPDATE accounts SET name = ?, name_set = 1, updated_at = ? WHERE low_id = ?",
                (name[:15], int(time.time()), low_id),
            )

    def select_brawler(self, low_id, brawler_id):
        with self.connect() as db:
            owned = db.execute(
                "SELECT 1 FROM brawlers WHERE account_low_id = ? AND brawler_id = ?",
                (low_id, brawler_id),
            ).fetchone()
            if owned:
                db.execute(
                    "UPDATE accounts SET selected_brawler = ?, updated_at = ? WHERE low_id = ?",
                    (brawler_id, int(time.time()), low_id),
                )
            return bool(owned)

    def claim_star_road(self, low_id, brawler_id):
        now = int(time.time())
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            loaded = self._load(db, low_id)
            if loaded is None:
                return False, "account"
            account, brawlers = loaded
            remaining = star_road_remaining(row["brawler_id"] for row in brawlers)
            if not remaining or remaining[0][0] != brawler_id:
                return False, "not-current"
            _, cost, _ = remaining[0]
            if account["credits"] < cost:
                return False, "credits"
            try:
                db.execute(
                    "INSERT INTO progression_actions(account_low_id, action_type, subject_id, amount, created_at) VALUES (?, 'star_road', ?, ?, ?)",
                    (low_id, brawler_id, cost, now),
                )
            except sqlite3.IntegrityError:
                return False, "already-claimed"
            db.execute(
                "UPDATE accounts SET credits = credits - ?, trophies = trophies + 5, highest_trophies = highest_trophies + 5, updated_at = ? WHERE low_id = ?",
                (cost, now, low_id),
            )
            db.execute(
                "INSERT INTO brawlers(account_low_id, brawler_id, card_id, unlocked_at) VALUES (?, ?, ?, ?)",
                (low_id, brawler_id, BRAWLER_CARD_IDS[brawler_id], now),
            )
            return True, cost

    def brawl_pass_credit_claims(self, low_id):
        with self.connect() as db:
            rows = db.execute(
                "SELECT subject_id FROM progression_actions WHERE account_low_id = ? AND action_type = 'brawl_pass_credit'",
                (low_id,),
            ).fetchall()
        return {
            (row["subject_id"] >> 16, (row["subject_id"] >> 8) & 0xFF, row["subject_id"] & 0xFF)
            for row in rows
        }

    def claim_brawl_pass_credit(self, low_id, season, reward_track, tier):
        amount = brawl_pass_credit_reward(season, reward_track, tier)
        if amount is None:
            return False, "not-credit"

        subject_id = (season << 16) | (reward_track << 8) | tier
        now = int(time.time())
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM accounts WHERE low_id = ?", (low_id,)).fetchone() is None:
                return False, "account"
            try:
                db.execute(
                    "INSERT INTO progression_actions(account_low_id, action_type, subject_id, amount, created_at) VALUES (?, 'brawl_pass_credit', ?, ?, ?)",
                    (low_id, subject_id, amount, now),
                )
            except sqlite3.IntegrityError:
                return False, "already-claimed"
            db.execute(
                "UPDATE accounts SET credits = credits + ?, updated_at = ? WHERE low_id = ?",
                (amount, now, low_id),
            )
        return True, amount

    def record_battle(self, low_id, map_id, result, rank, brawler_id):
        delta = trophy_delta(result, rank)
        won = rank == 1 if rank > 0 else result == 0
        tokens = 20 if won else 10
        credits = 20 if won else 8
        now = int(time.time())
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            brawler = db.execute(
                "SELECT trophies FROM brawlers WHERE account_low_id = ? AND brawler_id = ?",
                (low_id, brawler_id),
            ).fetchone()
            if brawler is None:
                return None
            applied_delta = max(5 - brawler["trophies"], delta)
            db.execute(
                "UPDATE brawlers SET trophies = trophies + ?, highest_trophies = MAX(highest_trophies, trophies + ?), mastery_points = mastery_points + ? WHERE account_low_id = ? AND brawler_id = ?",
                (applied_delta, applied_delta, max(0, applied_delta), low_id, brawler_id),
            )
            db.execute(
                "UPDATE accounts SET trophies = trophies + ?, highest_trophies = MAX(highest_trophies, trophies + ?), tokens = tokens + ?, credits = credits + ?, battle_count = battle_count + 1, wins = wins + ?, losses = losses + ?, updated_at = ? WHERE low_id = ?",
                (applied_delta, applied_delta, tokens, credits, int(won), int(not won and result != 2), now, low_id),
            )
            db.execute(
                "INSERT INTO battles(account_low_id, map_id, result, rank, brawler_id, trophy_delta, tokens, credits, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (low_id, map_id, result, rank, brawler_id, applied_delta, tokens, credits, now),
            )
            return {
                "trophy_delta": applied_delta,
                "tokens": tokens,
                "credits": credits,
                "won": won,
            }


database = GameDatabase()
