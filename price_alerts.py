"""Price alert system for stock notifications."""
import discord
import database
import market
import logging
import asyncio

logger = logging.getLogger(__name__)


async def check_and_trigger_alerts(bot):
    """Check all price alerts and trigger notifications."""
    async with database.get_db() as db:
        # Get all active alerts
        async with db.execute(
            """SELECT id, user_id, symbol, condition, target_price 
               FROM price_alerts"""
        ) as cursor:
            alerts = await cursor.fetchall()
        
        triggered = []
        for alert in alerts:
            alert_id, user_id, symbol, condition, target_price = alert
            
            # Get current price
            current_price = await market.market.get_price(symbol)
            if not current_price:
                continue
            
            # Check condition
            should_trigger = False
            if condition == 'above' and current_price >= target_price:
                should_trigger = True
            elif condition == 'below' and current_price <= target_price:
                should_trigger = True
            
            if should_trigger:
                # Send DM
                try:
                    user = await bot.fetch_user(user_id)
                    
                    embed = discord.Embed(
                        title="🔔 Price Alert Triggered!",
                        color=discord.Color.blue()
                    )
                    
                    from utils import spurs_to_cogs_display
                    from team_detection import get_team_name
                    
                    team_name = get_team_name(symbol)
                    condition_text = "above" if condition == "above" else "below"
                    
                    embed.add_field(
                        name=f"{symbol} - {team_name}",
                        value=f"Price is now {condition_text} your target!\n"
                              f"Current: {spurs_to_cogs_display(current_price)}\n"
                              f"Target: {spurs_to_cogs_display(target_price)}",
                        inline=False
                    )
                    
                    await user.send(embed=embed)
                    logger.info(f"Sent alert to user {user_id} for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Failed to send alert to {user_id}: {e}")
                
                # Delete alert
                await db.execute("DELETE FROM price_alerts WHERE id = ?", (alert_id,))
                triggered.append(alert_id)
        
        if triggered:
            await db.commit()
        
        return triggered
