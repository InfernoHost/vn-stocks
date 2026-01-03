"""Trade history tracking and analysis."""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import database
import utils
import team_detection


class HistoryCommands(commands.Cog):
    """Commands for viewing trade history."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="history", description="View your recent trade history")
    @app_commands.describe(
        days="Number of days to look back (1-30, default 7)",
        symbol="Filter by stock symbol (optional)"
    )
    async def history(
        self,
        interaction: discord.Interaction,
        days: int = 7,
        symbol: str = None
    ):
        """View trade history with P/L calculations."""
        # Validate days
        if days < 1 or days > 30:
            await interaction.response.send_message(
                "❌ Days must be between 1 and 30",
                ephemeral=True
            )
            return
        
        # Validate symbol
        if symbol:
            symbol = symbol.upper()
            from config import TEAMS
            if symbol not in TEAMS:
                await interaction.response.send_message(
                    f"❌ Invalid stock symbol. Valid symbols: {', '.join(TEAMS.keys())}",
                    ephemeral=True
                )
                return
        
        await interaction.response.defer()
        
        try:
            # Get transactions
            async with database.get_db() as db:
                cutoff = datetime.now() - timedelta(days=days)
                
                if symbol:
                    query = """
                        SELECT transaction_type, symbol, shares, price, timestamp
                        FROM transactions
                        WHERE user_id = ? AND symbol = ? AND timestamp >= ?
                        AND transaction_type IN ('buy', 'sell')
                        ORDER BY timestamp DESC
                        LIMIT 50
                    """
                    params = (interaction.user.id, symbol, cutoff.isoformat())
                else:
                    query = """
                        SELECT transaction_type, symbol, shares, price, timestamp
                        FROM transactions
                        WHERE user_id = ? AND timestamp >= ?
                        AND transaction_type IN ('buy', 'sell')
                        ORDER BY timestamp DESC
                        LIMIT 50
                    """
                    params = (interaction.user.id, cutoff.isoformat())
                
                async with db.execute(query, params) as cursor:
                    trades = await cursor.fetchall()
            
            if not trades:
                filter_text = f" for {symbol}" if symbol else ""
                await interaction.followup.send(
                    f"📜 No trades found in the last {days} day(s){filter_text}",
                    ephemeral=True
                )
                return
            
            # Build embed
            embed = discord.Embed(
                title=f"📜 Trade History - Last {days} Day(s)",
                description=f"Showing {len(trades)} trade(s)",
                color=discord.Color.blue()
            )
            
            # Group trades by symbol for summary
            symbol_stats = {}
            
            for trade_type, trade_symbol, shares, price, timestamp in trades:
                if trade_symbol not in symbol_stats:
                    symbol_stats[trade_symbol] = {
                        'buys': 0,
                        'sells': 0,
                        'buy_volume': 0,
                        'sell_volume': 0,
                        'buy_value': 0,
                        'sell_value': 0
                    }
                
                value = shares * price
                
                if trade_type == 'buy':
                    symbol_stats[trade_symbol]['buys'] += 1
                    symbol_stats[trade_symbol]['buy_volume'] += shares
                    symbol_stats[trade_symbol]['buy_value'] += value
                else:
                    symbol_stats[trade_symbol]['sells'] += 1
                    symbol_stats[trade_symbol]['sell_volume'] += shares
                    symbol_stats[trade_symbol]['sell_value'] += value
            
            # Summary field
            summary = ""
            total_bought = 0
            total_sold = 0
            
            for sym, stats in symbol_stats.items():
                team_name = team_detection.get_team_name(sym)
                
                if stats['buys'] > 0:
                    summary += f"📈 **{sym}**: {stats['buys']} buy(s), {stats['buy_volume']:,} shares\n"
                    total_bought += stats['buy_value']
                
                if stats['sells'] > 0:
                    summary += f"📉 **{sym}**: {stats['sells']} sell(s), {stats['sell_volume']:,} shares\n"
                    total_sold += stats['sell_value']
            
            embed.add_field(name="Summary", value=summary or "No trades", inline=False)
            
            # Recent trades (last 10)
            trades_text = ""
            for trade_type, trade_symbol, shares, price, timestamp in trades[:10]:
                team_name = team_detection.get_team_name(trade_symbol)
                emoji = "🟢" if trade_type == "buy" else "🔴"
                action = "Bought" if trade_type == "buy" else "Sold"
                
                # Parse timestamp
                dt = datetime.fromisoformat(timestamp)
                unix_timestamp = int(dt.timestamp())
                
                value = shares * price
                
                trades_text += f"{emoji} {action} {shares:,} {trade_symbol} @ {utils.spurs_to_cogs_display(price)}\n"
                trades_text += f"   Total: {utils.spurs_to_cogs_display(value)} • <t:{unix_timestamp}:R>\n"
            
            if trades_text:
                embed.add_field(name="Recent Trades", value=trades_text, inline=False)
            
            # Totals
            if total_bought > 0 or total_sold > 0:
                totals = f"**Total Bought:** {utils.spurs_to_cogs_display(total_bought)}\n"
                totals += f"**Total Sold:** {utils.spurs_to_cogs_display(total_sold)}\n"
                
                if total_sold > 0 and total_bought > 0:
                    net_pl = total_sold - total_bought
                    pl_emoji = "💰" if net_pl >= 0 else "📉"
                    pl_sign = "+" if net_pl >= 0 else ""
                    totals += f"{pl_emoji} **Net P/L:** {pl_sign}{utils.spurs_to_cogs_display(net_pl)}"
                
                embed.add_field(name="Totals", value=totals, inline=False)
            
            if len(trades) > 10:
                embed.set_footer(text=f"Showing 10 of {len(trades)} trades")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(HistoryCommands(bot))
