"""Candlestick chart commands."""
import discord
from discord import app_commands
from discord.ext import commands
import candlestick
import config


class CandlestickCommands(commands.Cog):
    """Commands for candlestick charts."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="candlestick", description="View candlestick chart for a stock")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, ROSE)",
        hours="Hours of data to show (default: 24)"
    )
    async def candlestick(
        self,
        interaction: discord.Interaction,
        symbol: str,
        hours: int = 24
    ):
        """Generate candlestick chart."""
        symbol = symbol.upper()
        
        # Validate symbol
        if symbol not in config.TEAMS:
            await interaction.response.send_message(
                f"❌ Invalid stock symbol. Valid symbols: {', '.join(config.TEAMS.keys())}",
                ephemeral=True
            )
            return
        
        # Validate hours
        if hours < 1 or hours > 168:  # Max 1 week
            await interaction.response.send_message(
                "❌ Hours must be between 1 and 168 (1 week)",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Generate chart
            chart_path = await candlestick.generate_candlestick_chart(symbol, hours)
            
            # Send
            file = discord.File(chart_path, filename=f'{symbol}_candlestick.png')
            
            embed = discord.Embed(
                title=f"📊 {symbol} Candlestick Chart",
                description=f"Last {hours} hour(s)",
                color=discord.Color.blue()
            )
            embed.set_image(url=f'attachment://{symbol}_candlestick.png')
            
            await interaction.followup.send(embed=embed, file=file)
            
        except ValueError as e:
            await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating chart: {str(e)}", ephemeral=True)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(CandlestickCommands(bot))
