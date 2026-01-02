"""Stock detail command with buy/sell buttons."""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os
import database
import market
import team_detection
import utils
import config
import graphing


class BuyModal(Modal, title='Buy Shares'):
    """Modal for buying shares."""
    
    shares_input = TextInput(
        label='Number of Shares',
        placeholder='Enter number of shares to buy',
        required=True,
        min_length=1,
        max_length=10
    )
    
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle buy submission."""
        try:
            shares = int(self.shares_input.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid number of shares!",
                ephemeral=True
            )
            return
        
        if shares <= 0:
            await interaction.response.send_message(
                "❌ Number of shares must be positive!",
                ephemeral=True
            )
            return
        
        user_id = interaction.user.id
        
        # Check if player exists
        player = await database.get_player(user_id)
        if not player:
            await interaction.response.send_message(
                "❌ You don't have an account! Use `/register` to create one.",
                ephemeral=True
            )
            return
        
        # ANTI-MANIPULATION: Check if user is a team member trying to trade their own stock
        if config.PREVENT_OWN_TEAM_TRADING and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(self.symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    await interaction.response.send_message(
                        f"🚫 **Anti-Manipulation Policy**\n"
                        f"You cannot buy your own team's stock to prevent insider trading!",
                        ephemeral=True
                    )
                    return
        
        # ANTI-MANIPULATION: Check if team has active trading cooldown
        cooldown_remaining = await database.check_team_trade_cooldown(self.symbol)
        if cooldown_remaining and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(self.symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    hours = cooldown_remaining // 3600
                    minutes = (cooldown_remaining % 3600) // 60
                    await interaction.response.send_message(
                        f"⏳ **Trading Cooldown**: **{hours}h {minutes}m** remaining",
                        ephemeral=True
                    )
                    return
        
        # Get current price
        price = await market.market.get_price(self.symbol)
        if price is None:
            await interaction.response.send_message(
                "❌ Unable to get stock price.",
                ephemeral=True
            )
            return
        
        # Calculate total cost
        total_cost = price * shares
        
        # Check if player has enough balance
        if player['balance'] < total_cost:
            needed = utils.format_price(total_cost)
            have = utils.format_price(player['balance'])
            await interaction.response.send_message(
                f"❌ Insufficient funds!\nNeed: **{needed}**\nHave: **{have}**",
                ephemeral=True
            )
            return
        
        # Execute trade
        balance_updated = await database.update_balance(user_id, -total_cost)
        if not balance_updated:
            await interaction.response.send_message(
                "❌ Transaction failed.",
                ephemeral=True
            )
            return
        
        portfolio_updated = await database.update_portfolio(user_id, self.symbol, shares, price, is_buy=True)
        if not portfolio_updated:
            # Rollback balance change
            await database.update_balance(user_id, total_cost)
            await interaction.response.send_message(
                "❌ Transaction failed.",
                ephemeral=True
            )
            return
        
        # Log transaction
        await database.log_transaction(
            user_id, 'BUY', self.symbol, total_cost, shares, price
        )
        
        # Success message
        team_name = team_detection.get_team_name(self.symbol)
        price_str = utils.format_price(price)
        total_str = utils.format_price(total_cost)
        
        embed = discord.Embed(
            title="✅ Purchase Complete",
            color=discord.Color.green()
        )
        embed.add_field(name="Stock", value=f"{self.symbol} - {team_name}", inline=False)
        embed.add_field(name="Shares", value=f"{shares}", inline=True)
        embed.add_field(name="Price per Share", value=price_str, inline=True)
        embed.add_field(name="Total Cost", value=total_str, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SellModal(Modal, title='Sell Shares'):
    """Modal for selling shares."""
    
    shares_input = TextInput(
        label='Number of Shares',
        placeholder='Enter number of shares to sell',
        required=True,
        min_length=1,
        max_length=10
    )
    
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle sell submission."""
        try:
            shares = int(self.shares_input.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid number of shares!",
                ephemeral=True
            )
            return
        
        if shares <= 0:
            await interaction.response.send_message(
                "❌ Number of shares must be positive!",
                ephemeral=True
            )
            return
        
        user_id = interaction.user.id
        
        # Check if player exists
        player = await database.get_player(user_id)
        if not player:
            await interaction.response.send_message(
                "❌ You don't have an account! Use `/register` to create one.",
                ephemeral=True
            )
            return
        
        # ANTI-MANIPULATION: Check if user is a team member trying to trade their own stock
        if config.PREVENT_OWN_TEAM_TRADING and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(self.symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    await interaction.response.send_message(
                        f"🚫 **Anti-Manipulation Policy**\n"
                        f"You cannot sell your own team's stock to prevent insider trading!",
                        ephemeral=True
                    )
                    return
        
        # ANTI-MANIPULATION: Check if team has active trading cooldown
        cooldown_remaining = await database.check_team_trade_cooldown(self.symbol)
        if cooldown_remaining and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(self.symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    hours = cooldown_remaining // 3600
                    minutes = (cooldown_remaining % 3600) // 60
                    await interaction.response.send_message(
                        f"⏳ **Trading Cooldown**: **{hours}h {minutes}m** remaining",
                        ephemeral=True
                    )
                    return
        
        # Check holdings
        holding = await database.get_holding(user_id, self.symbol)
        if not holding or holding['shares'] < shares:
            owned = holding['shares'] if holding else 0
            await interaction.response.send_message(
                f"❌ You don't have enough shares!\nOwned: **{owned}**\nTrying to sell: **{shares}**",
                ephemeral=True
            )
            return
        
        # Get current price
        price = await market.market.get_price(self.symbol)
        if price is None:
            await interaction.response.send_message(
                "❌ Unable to get stock price.",
                ephemeral=True
            )
            return
        
        # Calculate total proceeds
        total_proceeds = price * shares
        
        # Execute trade
        portfolio_updated = await database.update_portfolio(user_id, self.symbol, shares, price, is_buy=False)
        if not portfolio_updated:
            await interaction.response.send_message(
                "❌ Transaction failed.",
                ephemeral=True
            )
            return
        
        balance_updated = await database.update_balance(user_id, total_proceeds)
        if not balance_updated:
            # This shouldn't fail, but just in case
            await interaction.response.send_message(
                "❌ Transaction failed.",
                ephemeral=True
            )
            return
        
        # Log transaction
        await database.log_transaction(
            user_id, 'SELL', self.symbol, total_proceeds, shares, price
        )
        
        # Success message
        team_name = team_detection.get_team_name(self.symbol)
        price_str = utils.format_price(price)
        total_str = utils.format_price(total_proceeds)
        
        embed = discord.Embed(
            title="✅ Sale Complete",
            color=discord.Color.green()
        )
        embed.add_field(name="Stock", value=f"{self.symbol} - {team_name}", inline=False)
        embed.add_field(name="Shares", value=f"{shares}", inline=True)
        embed.add_field(name="Price per Share", value=price_str, inline=True)
        embed.add_field(name="Total Proceeds", value=total_str, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class StockView(View):
    """View with buy/sell buttons for a stock."""
    
    def __init__(self, symbol: str):
        super().__init__(timeout=300)  # 5 minute timeout
        self.symbol = symbol
    
    @discord.ui.button(label='Buy', style=discord.ButtonStyle.green, emoji='📈')
    async def buy_button(self, interaction: discord.Interaction, button: Button):
        """Handle buy button click."""
        modal = BuyModal(self.symbol)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Sell', style=discord.ButtonStyle.red, emoji='📉')
    async def sell_button(self, interaction: discord.Interaction, button: Button):
        """Handle sell button click."""
        modal = SellModal(self.symbol)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Refresh', style=discord.ButtonStyle.gray, emoji='🔄')
    async def refresh_button(self, interaction: discord.Interaction, button: Button):
        """Handle refresh button click."""
        await interaction.response.defer()
        
        # Get updated stock info
        embed, view, file = await create_stock_embed(self.symbol, interaction.user.id)
        
        if file:
            await interaction.edit_original_response(embed=embed, view=view, attachments=[file])
        else:
            await interaction.edit_original_response(embed=embed, view=view)


async def create_stock_embed(symbol: str, user_id: int):
    """Create embed with stock information, user holdings, and mini graph."""
    # Get stock info
    stock_info = await market.market.get_stock_info(symbol)
    if not stock_info:
        return None, None, None
    
    team_name = stock_info['team_name']
    current_price = stock_info['current_price']
    starting_price = stock_info['starting_price']
    volatility = stock_info['volatility']
    
    # Calculate price change from start
    price_change = current_price - starting_price
    price_change_pct = (price_change / starting_price) * 100 if starting_price > 0 else 0
    
    # Get user's holding
    holding = await database.get_holding(user_id, symbol)
    user_shares = holding['shares'] if holding else 0
    avg_cost = holding['avg_cost'] if holding else 0
    
    # Create embed
    embed = discord.Embed(
        title=f"📊 {symbol} - {team_name}",
        description="Gearfall Stock Exchange",
        color=0x5865F2
    )
    
    # Generate mini price graph
    graph_file = None
    try:
        graph_path = await graphing.generate_price_graph(symbol)
        graph_file = discord.File(graph_path, filename=f'{symbol}_chart.png')
        embed.set_image(url=f'attachment://{symbol}_chart.png')
    except:
        pass  # Skip graph if it fails
    
    # Current price
    price_str = utils.format_price(current_price)
    embed.add_field(name="💰 Current Price", value=f"**{price_str}**", inline=True)
    
    # Starting price
    start_str = utils.format_price(starting_price)
    embed.add_field(name="🏁 Starting Price", value=start_str, inline=True)
    
    # Change from start
    change_emoji = "📈" if price_change >= 0 else "📉"
    change_sign = "+" if price_change >= 0 else ""
    change_str = utils.format_price(abs(price_change))
    embed.add_field(
        name=f"{change_emoji} All-Time Change",
        value=f"{change_sign}{change_str}\n({price_change_pct:+.2f}%)",
        inline=True
    )
    
    # Volatility
    embed.add_field(name="📊 Volatility", value=f"{volatility * 100:.1f}%", inline=True)
    
    # Price history stats
    history = stock_info.get('price_history', [])
    if len(history) >= 2:
        recent_prices = [h['price'] for h in history[-10:]]
        if recent_prices:
            high_24h = max(recent_prices)
            low_24h = min(recent_prices)
            embed.add_field(name="📈 Recent High", value=utils.format_price(high_24h), inline=True)
            embed.add_field(name="📉 Recent Low", value=utils.format_price(low_24h), inline=True)
    
    # User holdings
    if user_shares > 0:
        pl, pl_pct = utils.calculate_profit_loss(avg_cost, current_price, user_shares)
        pl_emoji = "📈" if pl >= 0 else "📉"
        pl_sign = "+" if pl >= 0 else "-"
        pl_str = utils.format_price(abs(pl))
        
        current_value = utils.format_price(current_price * user_shares)
        avg_cost_str = utils.format_price(avg_cost)
        
        holdings_text = (
            f"**Shares Owned:** {user_shares}\n"
            f"**Avg Cost:** {avg_cost_str} per share\n"
            f"**Current Value:** {current_value}\n"
            f"**P&L:** {pl_emoji} {pl_sign}{pl_str} ({pl_pct:+.2f}%)"
        )
        embed.add_field(name="👤 Your Position", value=holdings_text, inline=False)
    else:
        embed.add_field(name="👤 Your Position", value="No shares owned - Click **Buy** to start trading!", inline=False)
    
    embed.set_footer(text="Click Buy/Sell buttons below to trade • Prices update every 3 minutes")
    
    # Create view with buttons
    view = StockView(symbol)
    
    return embed, view, graph_file


class StockCommands(commands.Cog):
    """Stock detail command."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stock", description="View detailed stock information with buy/sell options")
    @app_commands.describe(symbol="Stock symbol (e.g., STMP, VOC)")
    async def stock(self, interaction: discord.Interaction, symbol: str):
        """View stock details with interactive buy/sell buttons."""
        await interaction.response.defer(ephemeral=True)
        
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.followup.send(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        # Check if user is registered
        player = await database.get_player(interaction.user.id)
        if not player:
            await interaction.followup.send(
                "❌ You don't have an account! Use `/register` to create one.",
                ephemeral=True
            )
            return
        
        # Create embed and view
        embed, view, graph_file = await create_stock_embed(symbol, interaction.user.id)
        
        if not embed:
            await interaction.followup.send(
                "❌ Unable to load stock information.",
                ephemeral=True
            )
            return
        
        if graph_file:
            await interaction.followup.send(embed=embed, view=view, file=graph_file, ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(StockCommands(bot))
