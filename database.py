"""Database operations for player accounts and portfolios."""
import aiosqlite
import os
import time
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import config
import validators
from logger import logger


async def init_db():
    """Create database tables if they don't exist."""
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Players table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL
            )
        """)
        
        # Portfolio table (holdings)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                shares INTEGER NOT NULL DEFAULT 0,
                avg_cost INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, symbol),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        """)
        
        # Transactions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                symbol TEXT,
                amount INTEGER,
                shares INTEGER,
                price INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        """)
        
        # Admin actions log
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_user_id INTEGER,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Message cooldowns for market influence
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_cooldowns (
                user_id INTEGER PRIMARY KEY,
                last_message_time INTEGER NOT NULL
            )
        """)
        
        # Team trading cooldowns (anti-manipulation)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS team_trade_cooldowns (
                symbol TEXT PRIMARY KEY,
                cooldown_until INTEGER NOT NULL
            )
        """)
        
        # Create indexes for performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_players_balance ON players(balance DESC)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_admin_log_timestamp ON admin_log(timestamp)")
        
        await db.commit()


async def register_player(user_id: int) -> bool:
    """Register a new player. Returns True if successful, False if already exists."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        try:
            now = datetime.utcnow().isoformat()
            await db.execute(
                "INSERT INTO players (user_id, balance, created_at, last_activity) VALUES (?, ?, ?, ?)",
                (user_id, config.STARTING_BALANCE, now, now)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_player(user_id: int) -> Optional[Dict]:
    """Get player data."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def update_balance(user_id: int, amount: int) -> bool:
    """Update player balance. Amount can be positive or negative. Returns True if successful."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT balance FROM players WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            
            new_balance = row[0] + amount
            if new_balance < 0:
                return False
            
            await db.execute(
                "UPDATE players SET balance = ?, last_activity = ? WHERE user_id = ?",
                (new_balance, datetime.utcnow().isoformat(), user_id)
            )
            await db.commit()
            return True


async def get_portfolio(user_id: int) -> List[Dict]:
    """Get player's portfolio (all holdings)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM portfolio WHERE user_id = ? AND shares > 0 ORDER BY symbol",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_holding(user_id: int, symbol: str) -> Optional[Dict]:
    """Get player's holding for a specific stock."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?",
            (user_id, symbol)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def update_portfolio(user_id: int, symbol: str, shares: int, price: int, is_buy: bool) -> bool:
    """Update portfolio after buy/sell. Returns True if successful."""
    # Validate inputs to prevent overflow
    valid_transaction, error_msg = validators.validate_transaction(shares, price)
    if not valid_transaction:
        logger.error(f"Invalid transaction: {error_msg}")
        return False
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Use same connection for atomicity - prevents race conditions
        db.row_factory = aiosqlite.Row
        
        try:
            # Begin immediate transaction for exclusive lock
            await db.execute("BEGIN IMMEDIATE")
            
            # Get holding within same transaction
            async with db.execute(
                "SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?",
                (user_id, symbol)
            ) as cursor:
                row = await cursor.fetchone()
                holding = dict(row) if row else None
            
            if is_buy:
                if holding:
                    # Update average cost with overflow protection
                    current_value = holding['shares'] * holding['avg_cost']
                    new_value = shares * price
                    total_cost = current_value + new_value
                    new_shares = holding['shares'] + shares
                    
                    # Validate new total doesn't overflow
                    if total_cost > validators.MAX_BALANCE or new_shares > validators.MAX_SHARES:
                        await db.rollback()
                        return False
                    
                    new_avg_cost = total_cost // new_shares
                    
                    await db.execute(
                        "UPDATE portfolio SET shares = ?, avg_cost = ? WHERE user_id = ? AND symbol = ?",
                        (new_shares, new_avg_cost, user_id, symbol)
                    )
                else:
                    # Create new holding
                    await db.execute(
                        "INSERT INTO portfolio (user_id, symbol, shares, avg_cost) VALUES (?, ?, ?, ?)",
                        (user_id, symbol, shares, price)
                    )
            else:
                # Sell
                if not holding or holding['shares'] < shares:
                    await db.rollback()
                    return False
                
                new_shares = holding['shares'] - shares
                await db.execute(
                    "UPDATE portfolio SET shares = ? WHERE user_id = ? AND symbol = ?",
                    (new_shares, user_id, symbol)
                )
            
            await db.commit()
            return True
            
        except Exception as e:
            # Rollback on any error
            await db.rollback()
            logger.error(f"Portfolio update failed for user {user_id}, symbol {symbol}: {e}")
            return False


async def log_transaction(user_id: int, transaction_type: str, symbol: Optional[str] = None,
                         amount: Optional[int] = None, shares: Optional[int] = None,
                         price: Optional[int] = None):
    """Log a transaction."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO transactions 
               (user_id, transaction_type, symbol, amount, shares, price, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, transaction_type, symbol, amount, shares, price, datetime.utcnow().isoformat())
        )
        await db.commit()


async def log_admin_action(admin_id: int, action: str, target_user_id: Optional[int] = None,
                          details: Optional[str] = None):
    """Log an admin action."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO admin_log (admin_id, action, target_user_id, details, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (admin_id, action, target_user_id, details, datetime.utcnow().isoformat())
        )
        await db.commit()


async def get_leaderboard(limit: int = 10) -> List[Tuple[int, int]]:
    """Get leaderboard of richest players. Returns list of (user_id, balance)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, balance FROM players ORDER BY balance DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return rows


async def check_message_cooldown(user_id: int, cooldown_seconds: int) -> bool:
    """Check if user is on cooldown. Returns True if can send influence message."""
    current_time = int(time.time())
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT last_message_time FROM message_cooldowns WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if not row:
                # First message
                await db.execute(
                    "INSERT INTO message_cooldowns (user_id, last_message_time) VALUES (?, ?)",
                    (user_id, current_time)
                )
                await db.commit()
                return True
            
            last_time = row[0]
            if current_time - last_time >= cooldown_seconds:
                # Update last message time
                await db.execute(
                    "UPDATE message_cooldowns SET last_message_time = ? WHERE user_id = ?",
                    (current_time, user_id)
                )
                await db.commit()
                return True
            
            return False


async def set_team_trade_cooldown(symbol: str, cooldown_seconds: int):
    """Set a trading cooldown for a specific team after admin events."""
    cooldown_until = int(time.time()) + cooldown_seconds
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO team_trade_cooldowns (symbol, cooldown_until)
               VALUES (?, ?)""",
            (symbol, cooldown_until)
        )
        await db.commit()


async def check_team_trade_cooldown(symbol: str) -> Optional[int]:
    """
    Check if a team has an active trading cooldown.
    Returns remaining seconds if on cooldown, None otherwise.
    """
    current_time = int(time.time())
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT cooldown_until FROM team_trade_cooldowns WHERE symbol = ?",
            (symbol,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            cooldown_until = row[0]
            if current_time < cooldown_until:
                return cooldown_until - current_time
            
            # Cooldown expired, remove it
            await db.execute(
                "DELETE FROM team_trade_cooldowns WHERE symbol = ?",
                (symbol,)
            )
            await db.commit()
            return None
