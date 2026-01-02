"""Graph commands for viewing price history."""
import discord
from discord import app_commands
from discord.ext import commands
import graphing
import team_detection


class GraphCommands(commands.Cog):
    """Commands for viewing price graphs."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="graph", description="View price history graph for a stock")
    @app_commands.describe(symbol="Stock symbol (e.g., STMP, VOC)")
    async def graph(self, interaction: discord.Interaction, symbol: str):
        """Generate and display price history graph."""
        await interaction.response.defer()
        
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.followup.send(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        try:
            # Generate graph
            graph_path = await graphing.generate_price_graph(symbol)
            
            # Send graph
            team_name = team_detection.get_team_name(symbol)
            file = discord.File(graph_path, filename=f'{symbol}_graph.png')
            
            embed = discord.Embed(
                title=f"📈 {symbol} - {team_name}",
                description="Price history",
                color=discord.Color.blue()
            )
            embed.set_image(url=f'attachment://{symbol}_graph.png')
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to generate graph: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="compare", description="Compare price history of multiple stocks")
    @app_commands.describe(
        symbol1="First stock symbol",
        symbol2="Second stock symbol",
        symbol3="Third stock symbol (optional)",
        symbol4="Fourth stock symbol (optional)"
    )
    async def compare(
        self,
        interaction: discord.Interaction,
        symbol1: str,
        symbol2: str,
        symbol3: str = None,
        symbol4: str = None
    ):
        """Generate comparison graph for multiple stocks."""
        await interaction.response.defer()
        
        # Collect and validate symbols
        symbols = [symbol1, symbol2]
        if symbol3:
            symbols.append(symbol3)
        if symbol4:
            symbols.append(symbol4)
        
        # Normalize and validate
        normalized_symbols = []
        for symbol in symbols:
            symbol = team_detection.normalize_symbol(symbol)
            if not team_detection.validate_symbol(symbol):
                await interaction.followup.send(
                    f"❌ Invalid stock symbol: **{symbol}**",
                    ephemeral=True
                )
                return
            normalized_symbols.append(symbol)
        
        try:
            # Generate comparison graph
            graph_path = await graphing.generate_comparison_graph(normalized_symbols)
            
            # Send graph
            file = discord.File(graph_path, filename='comparison_graph.png')
            
            embed = discord.Embed(
                title="📊 Stock Comparison",
                description=f"Comparing: {', '.join(normalized_symbols)}",
                color=discord.Color.blue()
            )
            embed.set_image(url='attachment://comparison_graph.png')
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to generate comparison graph: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(GraphCommands(bot))
