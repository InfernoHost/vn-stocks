"""Limit orders system for automated trading at target prices."""
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config
import database
import market
from logger import logger


async def create_limit_order(user_id: int, symbol: str, order_type: str, shares: int, target_price: int, expires_hours: int = 24) -> int:
    """
    Create a limit order.
    
    Args:
        user_id: Player ID
        symbol: Stock symbol
        order_type: 'buy' or 'sell'
        shares: Number of shares
        target_price: Price to execute at (in Spurs)
        expires_hours: Hours until order expires
    
    Returns:
        Order ID
    """
    async with aiosqlite.connect(config.DB_PATH) as db:
        now = datetime.utcnow()
        expires = now + timedelta(hours=expires_hours)
        
        cursor = await db.execute(
            """INSERT INTO limit_orders 
               (user_id, symbol, order_type, shares, target_price, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, symbol, order_type, shares, target_price, now.isoformat(), expires.isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def get_user_orders(user_id: int) -> List[Dict]:
    """Get all active orders for a user."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM limit_orders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def cancel_order(order_id: int, user_id: int) -> bool:
    """Cancel a limit order. Returns True if successful."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM limit_orders WHERE id = ? AND user_id = ?",
            (order_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def check_and_execute_orders():
    """Check all limit orders and execute those that meet conditions."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get all active orders
        async with db.execute("SELECT * FROM limit_orders") as cursor:
            orders = await cursor.fetchall()
        
        now = datetime.utcnow()
        executed = []
        
        for order_row in orders:
            order = dict(order_row)
            
            # Check expiration
            if order['expires_at']:
                expires = datetime.fromisoformat(order['expires_at'])
                if now > expires:
                    await db.execute("DELETE FROM limit_orders WHERE id = ?", (order['id'],))
                    continue
            
            # Get current price
            current_price = await market.market.get_price(order['symbol'])
            if not current_price:
                continue
            
            # Check if condition met
            should_execute = False
            if order['order_type'] == 'buy' and current_price <= order['target_price']:
                should_execute = True
            elif order['order_type'] == 'sell' and current_price >= order['target_price']:
                should_execute = True
            
            if should_execute:
                # Try to execute the trade
                success = False
                if order['order_type'] == 'buy':
                    # Check balance
                    cost = current_price * order['shares']
                    balance = await database.get_balance(order['user_id'])
                    if balance >= cost:
                        await database.update_balance(order['user_id'], -cost)
                        await database.add_shares(order['user_id'], order['symbol'], order['shares'], current_price)
                        success = True
                else:  # sell
                    # Check shares
                    shares = await database.get_shares(order['user_id'], order['symbol'])
                    if shares >= order['shares']:
                        revenue = current_price * order['shares']
                        await database.remove_shares(order['user_id'], order['symbol'], order['shares'])
                        await database.update_balance(order['user_id'], revenue)
                        success = True
                
                if success:
                    # Log transaction
                    await database.log_transaction(
                        order['user_id'],
                        order['order_type'],
                        order['symbol'],
                        current_price * order['shares'],
                        order['shares'],
                        current_price
                    )
                    
                    # Delete order
                    await db.execute("DELETE FROM limit_orders WHERE id = ?", (order['id'],))
                    
                    executed.append({
                        'user_id': order['user_id'],
                        'order': order,
                        'price': current_price
                    })
        
        await db.commit()
        return executed
