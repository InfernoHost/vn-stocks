"""Price alert commands."""
import discord
from discord import app_commands
from discord.ext import commands
import database
import market
import utils
import config
import team_detection


class AlertCommands(commands.Cog):
    """Commands for price alerts."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="alert", description="Set a price alert for a stock")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, ROSE)",
        condition="Trigger when price goes above or below target",
        price="Target price in Cogs (e.g., 10.5)"
    )
    @app_commands.choices(condition=[
        app_commands.Choice(name="Above", value="above"),
        app_commands.Choice(name="Below", value="below")
    ])
    async def alert(
        self,
        interaction: discord.Interaction,
        symbol: str,
        condition: str,
        price: float
    ):
        """Set a price alert."""
        symbol = symbol.upper()
        
        # Validate symbol
        if symbol not in config.TEAMS:
            await interaction.response.send_message(
                f"❌ Invalid stock symbol. Valid symbols: {', '.join(config.TEAMS.keys())}",
                ephemeral=True
            )
            return
        
        # Validate price
        target_price = utils.cogs_to_spurs(price)
        if target_price <= 0:
            await interaction.response.send_message("❌ Price must be positive", ephemeral=True)
            return
        
        # Check if user has too many alerts
        async with database.get_db() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM price_alerts WHERE user_id = ?",
                (interaction.user.id,)
            ) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count >= 10:
                await interaction.response.send_message(
                    "❌ You can only have up to 10 active alerts. Use `/alerts` to view and `/removealert` to delete.",
                    ephemeral=True
                )
                return
            
            # Create alert
            await db.execute(
                """INSERT INTO price_alerts (user_id, symbol, condition, target_price, created_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                (interaction.user.id, symbol, condition, target_price)
            )
            await db.commit()
        
        # Success response
        team_name = team_detection.get_team_name(symbol)
        current_price = await market.market.get_price(symbol)
        
        embed = discord.Embed(
            title="🔔 Alert Created",
            color=discord.Color.blue()
        )
        
        condition_text = "rises above" if condition == "above" else "falls below"
        embed.add_field(
            name=f"{symbol} - {team_name}",
            value=f"You'll be notified when the price {condition_text} {utils.spurs_to_cogs_display(target_price)}\n"
                  f"Current price: {utils.spurs_to_cogs_display(current_price)}",
            inline=False
        )
        
        embed.set_footer(text="You'll receive a DM when the alert triggers")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="alerts", description="View your active price alerts")
    async def alerts(self, interaction: discord.Interaction):
        """View active alerts."""
        async with database.get_db() as db:
            async with db.execute(
                """SELECT id, symbol, condition, target_price, created_at
                   FROM price_alerts
                   WHERE user_id = ?
                   ORDER BY created_at DESC""",
                (interaction.user.id,)
            ) as cursor:
                alerts = await cursor.fetchall()
        
        if not alerts:
            await interaction.response.send_message("🔔 You have no active alerts", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🔔 Your Price Alerts ({len(alerts)}/10)",
            color=discord.Color.blue()
        )
        
        for alert_id, symbol, condition, target_price, created_at in alerts:
            team_name = team_detection.get_team_name(symbol)
            current_price = await market.market.get_price(symbol)
            
            condition_text = "Above" if condition == "above" else "Below"
            
            # Parse timestamp string
            from datetime import datetime
            dt = datetime.fromisoformat(created_at)
            
            embed.add_field(
                name=f"Alert #{alert_id} - {symbol}",
                value=f"**{team_name}**\n"
                      f"Trigger: {condition_text} {utils.spurs_to_cogs_display(target_price)}\n"
                      f"Current: {utils.spurs_to_cogs_display(current_price)}\n"
                      f"Created: <t:{int(dt.timestamp())}:R>",
                inline=True
            )
        
        embed.set_footer(text="Use /removealert <id> to delete an alert")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removealert", description="Remove a price alert")
    @app_commands.describe(alert_id="Alert ID from /alerts")
    async def removealert(self, interaction: discord.Interaction, alert_id: int):
        """Remove an alert."""
        async with database.get_db() as db:
            # Check if alert exists and belongs to user
            async with db.execute(
                "SELECT symbol FROM price_alerts WHERE id = ? AND user_id = ?",
                (alert_id, interaction.user.id)
            ) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                await interaction.response.send_message(
                    "❌ Alert not found or doesn't belong to you",
                    ephemeral=True
                )
                return
            
            symbol = result[0]
            
            # Delete alert
            await db.execute(
                "DELETE FROM price_alerts WHERE id = ? AND user_id = ?",
                (alert_id, interaction.user.id)
            )
            await db.commit()
        
        await interaction.response.send_message(
            f"✅ Removed alert #{alert_id} for {symbol}",
            ephemeral=True
        )


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(AlertCommands(bot))
