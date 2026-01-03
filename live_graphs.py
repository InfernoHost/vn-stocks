"""Live graph system for auto-updating stock graphs."""
import asyncio
import discord
from datetime import datetime
from typing import Dict, Optional
import graphing


class LiveGraph:
    """Manages a live-updating stock graph."""
    
    def __init__(self, message: discord.Message, symbol: str, interaction_user_id: int):
        self.message = message
        self.symbol = symbol
        self.interaction_user_id = interaction_user_id
        self.last_interaction = datetime.now()
        self.is_active = True
        self.update_task: Optional[asyncio.Task] = None
    
    def keep_alive(self):
        """Reset the inactivity timer."""
        self.last_interaction = datetime.now()
    
    def seconds_since_last_interaction(self) -> float:
        """Get seconds since last interaction."""
        return (datetime.now() - self.last_interaction).total_seconds()
    
    async def stop(self):
        """Stop the live graph updates."""
        self.is_active = False
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()


class LiveGraphManager:
    """Manages all active live graphs."""
    
    def __init__(self):
        self.live_graphs: Dict[int, LiveGraph] = {}  # message_id -> LiveGraph
    
    def add_graph(self, message: discord.Message, symbol: str, user_id: int) -> LiveGraph:
        """Add a new live graph."""
        live_graph = LiveGraph(message, symbol, user_id)
        self.live_graphs[message.id] = live_graph
        return live_graph
    
    def get_graph(self, message_id: int) -> Optional[LiveGraph]:
        """Get a live graph by message ID."""
        return self.live_graphs.get(message_id)
    
    def remove_graph(self, message_id: int):
        """Remove a live graph."""
        if message_id in self.live_graphs:
            del self.live_graphs[message_id]
    
    async def update_graph_loop(self, live_graph: LiveGraph, update_interval: int = 30):
        """
        Continuously update a graph until inactive.
        
        Args:
            live_graph: The LiveGraph to update
            update_interval: Seconds between updates (default 30)
        """
        try:
            while live_graph.is_active:
                # Check if inactive for 120 seconds
                if live_graph.seconds_since_last_interaction() > 120:
                    # Add stopped indicator to graph
                    embed = live_graph.message.embeds[0]
                    embed.description = f"Price history (Updates stopped - inactive)"
                    embed.color = discord.Color.greyple()
                    
                    try:
                        await live_graph.message.edit(embed=embed)
                    except discord.NotFound:
                        pass  # Message was deleted
                    
                    self.remove_graph(live_graph.message.id)
                    return
                
                # Wait for update interval
                await asyncio.sleep(update_interval)
                
                if not live_graph.is_active:
                    break
                
                # Generate new graph
                try:
                    graph_path = await graphing.generate_price_graph(live_graph.symbol)
                    
                    # Update message with new graph
                    file = discord.File(graph_path, filename=f'{live_graph.symbol}_graph.png')
                    
                    embed = live_graph.message.embeds[0]
                    embed.description = f"Price history (Live • Updates every {update_interval}s)"
                    embed.set_image(url=f'attachment://{live_graph.symbol}_graph.png')
                    embed.timestamp = datetime.now()
                    
                    await live_graph.message.edit(embed=embed, attachments=[file])
                    
                except discord.NotFound:
                    # Message was deleted
                    self.remove_graph(live_graph.message.id)
                    return
                except Exception as e:
                    print(f"Error updating live graph: {e}")
                    # Continue trying on errors
        
        except asyncio.CancelledError:
            self.remove_graph(live_graph.message.id)
        except Exception as e:
            print(f"Fatal error in live graph loop: {e}")
            self.remove_graph(live_graph.message.id)


# Global manager instance
live_graph_manager = LiveGraphManager()


class LiveGraphView(discord.ui.View):
    """View with controls for live graphs."""
    
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        
    @discord.ui.button(label="🔄 Keep Alive", style=discord.ButtonStyle.primary, custom_id="graph_keep_alive")
    async def keep_alive_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle keep alive button click."""
        live_graph = live_graph_manager.get_graph(interaction.message.id)
        
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
    
    @discord.ui.button(label="⏹️ Stop Updates", style=discord.ButtonStyle.danger, custom_id="graph_stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle stop button click."""
        live_graph = live_graph_manager.get_graph(interaction.message.id)
        
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
        live_graph_manager.remove_graph(interaction.message.id)
        
        # Update embed to show stopped status
        embed = interaction.message.embeds[0]
        embed.description = "Price history (Updates stopped)"
        embed.color = discord.Color.greyple()
        
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message(
            "⏹️ Graph updates stopped.",
            ephemeral=True
        )
