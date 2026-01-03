"""Limit order commands."""
import discord
from discord import app_commands
from discord.ext import commands
import limit_orders
import database
import team_detection
import utils
import config


class LimitOrderCommands(commands.Cog):
    """Commands for limit orders."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="limitbuy", description="Place a limit buy order")
    @app_commands.describe(
        symbol="Stock symbol",
        shares="Number of shares",
        price="Target price per share (in Cogs)"
    )
    async def limitbuy(self, interaction: discord.Interaction, symbol: str, shares: int, price: float):
        """Place a limit buy order that executes when price drops to target."""
        symbol = team_detection.normalize_symbol(symbol)
        
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(f"❌ Invalid symbol: **{symbol}**", ephemeral=True)
            return
        
        if shares <= 0:
            await interaction.response.send_message("❌ Shares must be positive", ephemeral=True)
            return
        
        if price <= 0:
            await interaction.response.send_message("❌ Price must be positive", ephemeral=True)
            return
        
        target_price = utils.cogs_to_spurs(price)
        cost = target_price * shares
        
        # Check if user has enough balance
        balance = await database.get_balance(interaction.user.id)
        if balance < cost:
            await interaction.response.send_message(
                f"❌ Not enough balance. Need {utils.spurs_to_cogs_display(cost)}, have {utils.spurs_to_cogs_display(balance)}",
                ephemeral=True
            )
            return
        
        # Create order
        order_id = await limit_orders.create_limit_order(
            interaction.user.id,
            symbol,
            'buy',
            shares,
            target_price
        )
        
        team_name = team_detection.get_team_name(symbol)
        embed = discord.Embed(
            title="✅ Limit Buy Order Placed",
            description=f"Order will execute when **{symbol} - {team_name}** drops to or below **{utils.spurs_to_cogs_display(target_price)}/share**",
            color=discord.Color.green()
        )
        embed.add_field(name="Shares", value=f"{shares:,}")
        embed.add_field(name="Total Cost", value=utils.spurs_to_cogs_display(cost))
        embed.add_field(name="Order ID", value=f"`{order_id}`")
        embed.set_footer(text="Order expires in 24 hours • Use /orders to view • /cancelorder to cancel")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="limitsell", description="Place a limit sell order")
    @app_commands.describe(
        symbol="Stock symbol",
        shares="Number of shares",
        price="Target price per share (in Cogs)"
    )
    async def limitsell(self, interaction: discord.Interaction, symbol: str, shares: int, price: float):
        """Place a limit sell order that executes when price rises to target."""
        symbol = team_detection.normalize_symbol(symbol)
        
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(f"❌ Invalid symbol: **{symbol}**", ephemeral=True)
            return
        
        if shares <= 0:
            await interaction.response.send_message("❌ Shares must be positive", ephemeral=True)
            return
        
        if price <= 0:
            await interaction.response.send_message("❌ Price must be positive", ephemeral=True)
            return
        
        # Check if user has enough shares
        owned = await database.get_shares(interaction.user.id, symbol)
        if owned < shares:
            await interaction.response.send_message(
                f"❌ Not enough shares. Need {shares:,}, have {owned:,}",
                ephemeral=True
            )
            return
        
        target_price = utils.cogs_to_spurs(price)
        revenue = target_price * shares
        
        # Create order
        order_id = await limit_orders.create_limit_order(
            interaction.user.id,
            symbol,
            'sell',
            shares,
            target_price
        )
        
        team_name = team_detection.get_team_name(symbol)
        embed = discord.Embed(
            title="✅ Limit Sell Order Placed",
            description=f"Order will execute when **{symbol} - {team_name}** rises to or above **{utils.spurs_to_cogs_display(target_price)}/share**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Shares", value=f"{shares:,}")
        embed.add_field(name="Total Revenue", value=utils.spurs_to_cogs_display(revenue))
        embed.add_field(name="Order ID", value=f"`{order_id}`")
        embed.set_footer(text="Order expires in 24 hours • Use /orders to view • /cancelorder to cancel")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="orders", description="View your active limit orders")
    async def orders(self, interaction: discord.Interaction):
        """View all active limit orders."""
        orders = await limit_orders.get_user_orders(interaction.user.id)
        
        if not orders:
            await interaction.response.send_message("📋 You have no active limit orders", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 {interaction.user.display_name}'s Limit Orders",
            description=f"{len(orders)} active order(s)",
            color=discord.Color.blue()
        )
        
        for order in orders[:10]:  # Show max 10
            symbol = order['symbol']
            order_type = order['order_type']
            shares = order['shares']
            target_price = order['target_price']
            order_id = order['id']
            
            # Parse created_at timestamp
            from datetime import datetime
            created = datetime.fromisoformat(order['created_at'])
            
            emoji = "🟢" if order_type == "buy" else "🔴"
            action = "Buy" if order_type == "buy" else "Sell"
            team_name = team_detection.get_team_name(symbol)
            
            embed.add_field(
                name=f"{emoji} Order #{order_id} - {symbol}",
                value=f"{action} {shares:,} shares at {utils.spurs_to_cogs_display(target_price)}\n"
                      f"{team_name} • <t:{int(created.timestamp())}:R>",
                inline=True
            )
        
        embed.set_footer(text=f"Showing {min(len(orders), 10)} of {len(orders)} orders • Use /cancelorder <id> to cancel")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="cancelorder", description="Cancel a limit order")
    @app_commands.describe(order_id="Order ID to cancel")
    async def cancelorder(self, interaction: discord.Interaction, order_id: int):
        """Cancel a limit order."""
        success = await limit_orders.cancel_order(order_id, interaction.user.id)
        
        if success:
            await interaction.response.send_message(f"✅ Canceled order **#{order_id}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Order **#{order_id}** not found or not yours", ephemeral=True)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(LimitOrderCommands(bot))
