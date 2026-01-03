"""Watchlist system for tracking stocks."""
import discord
from discord import app_commands
from discord.ext import commands
import database
import market
import utils
import config
import team_detection


class WatchlistCommands(commands.Cog):
    """Commands for managing watchlist."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="watch", description="Add a stock to your watchlist")
    @app_commands.describe(symbol="Stock symbol to watch (e.g., STMP, ROSE)")
    async def watch(self, interaction: discord.Interaction, symbol: str):
        """Add stock to watchlist."""
        symbol = symbol.upper()
        
        # Validate symbol
        if symbol not in config.TEAMS:
            await interaction.response.send_message(
                f"❌ Invalid stock symbol. Valid symbols: {', '.join(config.TEAMS.keys())}",
                ephemeral=True
            )
            return
        
        async with database.get_db() as db:
            # Check if already watching
            async with db.execute(
                "SELECT 1 FROM watchlist WHERE user_id = ? AND symbol = ?",
                (interaction.user.id, symbol)
            ) as cursor:
                exists = await cursor.fetchone()
            
            if exists:
                await interaction.response.send_message(
                    f"❌ You're already watching {symbol}",
                    ephemeral=True
                )
                return
            
            # Check watchlist limit
            async with db.execute(
                "SELECT COUNT(*) FROM watchlist WHERE user_id = ?",
                (interaction.user.id,)
            ) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count >= 10:
                await interaction.response.send_message(
                    "❌ Watchlist is full (max 10 stocks). Use `/unwatch` to remove stocks.",
                    ephemeral=True
                )
                return
            
            # Add to watchlist
            await db.execute(
                """INSERT INTO watchlist (user_id, symbol, added_at)
                   VALUES (?, ?, datetime('now'))""",
                (interaction.user.id, symbol)
            )
            await db.commit()
        
        # Success response
        team_name = team_detection.get_team_name(symbol)
        current_price = await market.market.get_price(symbol)
        
        embed = discord.Embed(
            title="👁️ Added to Watchlist",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f"{symbol} - {team_name}",
            value=f"Current price: {utils.spurs_to_cogs_display(current_price)}\n"
                  f"You'll see this stock highlighted in `/market`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unwatch", description="Remove a stock from your watchlist")
    @app_commands.describe(symbol="Stock symbol to stop watching")
    async def unwatch(self, interaction: discord.Interaction, symbol: str):
        """Remove stock from watchlist."""
        symbol = symbol.upper()
        
        async with database.get_db() as db:
            # Check if watching
            async with db.execute(
                "SELECT 1 FROM watchlist WHERE user_id = ? AND symbol = ?",
                (interaction.user.id, symbol)
            ) as cursor:
                exists = await cursor.fetchone()
            
            if not exists:
                await interaction.response.send_message(
                    f"❌ You're not watching {symbol}",
                    ephemeral=True
                )
                return
            
            # Remove from watchlist
            await db.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND symbol = ?",
                (interaction.user.id, symbol)
            )
            await db.commit()
        
        await interaction.response.send_message(
            f"✅ Removed {symbol} from watchlist",
            ephemeral=True
        )
    
    @app_commands.command(name="watchlist", description="View your watchlist")
    async def watchlist(self, interaction: discord.Interaction):
        """View watchlist with current prices."""
        async with database.get_db() as db:
            async with db.execute(
                """SELECT symbol, added_at FROM watchlist
                   WHERE user_id = ?
                   ORDER BY added_at DESC""",
                (interaction.user.id,)
            ) as cursor:
                watched = await cursor.fetchall()
        
        if not watched:
            await interaction.response.send_message(
                "👁️ Your watchlist is empty. Use `/watch <symbol>` to add stocks.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"👁️ Your Watchlist ({len(watched)}/10)",
            color=discord.Color.blue()
        )
        
        for symbol, added_at in watched:
            team_name = team_detection.get_team_name(symbol)
            current_price = await market.market.get_price(symbol)
            
            # Get price history for 24h change
            from market import market as market_instance
            history = await market_instance.get_price_history(symbol, limit=48)  # ~24 hours of 30min intervals
            
            if len(history) >= 2:
                old_price = history[0]['price']
                change = current_price - old_price
                change_pct = (change / old_price * 100) if old_price > 0 else 0
                
                change_emoji = "📈" if change >= 0 else "📉"
                change_sign = "+" if change >= 0 else ""
                change_text = f"{change_emoji} {change_sign}{change_pct:.1f}% (24h)"
            else:
                change_text = "📊 Insufficient data"
            
            embed.add_field(
                name=f"{symbol} - {team_name}",
                value=f"**Price:** {utils.spurs_to_cogs_display(current_price)}\n{change_text}",
                inline=True
            )
        
        embed.set_footer(text="Use /unwatch <symbol> to remove stocks")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(WatchlistCommands(bot))
