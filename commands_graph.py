"""Graph commands for viewing price history."""
import discord
from discord import app_commands
from discord.ext import commands
import graphing
import team_detection
from live_graphs import live_graph_manager


class KeepAliveButton(discord.ui.Button):
    """Button to keep a live graph active."""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="🔄 Keep Alive",
            custom_id="graph_keep_alive"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle keep alive button click."""
        live_graph = live_graph_manager.get_graph(self.view.message.id)
        
        if not live_graph:
            await interaction.response.send_message(
                "⏹️ This graph is no longer updating.",
                ephemeral=True
            )
            return
        
        # Only the user who created the graph can keep it alive
        if interaction.user.id != live_graph.interaction_user_id:
            await interaction.response.send_message(
                "❌ Only the user who created this graph can keep it alive.",
                ephemeral=True
            )
            return
        
        live_graph.keep_alive()
        await interaction.response.send_message(
            f"✅ Graph will continue updating for another 120 seconds.",
            ephemeral=True
        )


class StopButton(discord.ui.Button):
    """Button to stop a live graph."""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="⏹️ Stop Updates",
            custom_id="graph_stop"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle stop button click."""
        live_graph = live_graph_manager.get_graph(self.view.message.id)
        
        if not live_graph:
            await interaction.response.send_message(
                "⏹️ This graph is no longer updating.",
                ephemeral=True
            )
            return
        
        # Only the user who created the graph can stop it
        if interaction.user.id != live_graph.interaction_user_id:
            await interaction.response.send_message(
                "❌ Only the user who created this graph can stop it.",
                ephemeral=True
            )
            return
        
        await live_graph.stop()
        live_graph_manager.remove_graph(self.view.message.id)
        
        # Update embed to show stopped status
        embed = self.view.message.embeds[0]
        embed.description = "Price history (Updates stopped)"
        embed.color = discord.Color.greyple()
        
        await self.view.message.edit(embed=embed, view=None)
        await interaction.response.send_message(
            "⏹️ Graph updates stopped.",
            ephemeral=True
        )


class LiveGraphView(discord.ui.View):
    """View with controls for live graphs."""
    
    def __init__(self):
        super().__init__(timeout=None)  # No timeout
        self.add_item(KeepAliveButton())
        self.add_item(StopButton())


class GraphCommands(commands.Cog):
    """Commands for viewing price graphs."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="graph", description="View price history graph for a stock")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, VOC)",
        live="Enable live updates (default: True)"
    )
    async def graph(self, interaction: discord.Interaction, symbol: str, live: bool = True):
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
            
            description = "Price history"
            if live:
                description += " (Live • Updates every 30s)"
            
            embed = discord.Embed(
                title=f"📈 {symbol} - {team_name}",
                description=description,
                color=discord.Color.green() if live else discord.Color.blue()
            )
            embed.set_image(url=f'attachment://{symbol}_graph.png')
            
            if live:
                embed.set_footer(text="Click 'Keep Alive' to extend updates • Auto-stops after 120s of inactivity")
            
            # Send with or without controls
            view = LiveGraphView() if live else None
            message = await interaction.followup.send(embed=embed, file=file, view=view)
            
            # Start live updates if enabled
            if live:
                live_graph = live_graph_manager.add_graph(message, symbol, interaction.user.id)
                live_graph.update_task = self.bot.loop.create_task(
                    live_graph_manager.update_graph_loop(live_graph, update_interval=30)
                )
            
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
