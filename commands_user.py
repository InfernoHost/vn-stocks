"""User commands for the economy bot."""
import discord
from discord import app_commands
from discord.ext import commands
import database
import market
import team_detection
import utils
import config


class UserCommands(commands.Cog):
    """User-facing trading commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="register", description="Create a trading account")
    async def register(self, interaction: discord.Interaction):
        """Register a new player account."""
        user_id = interaction.user.id
        
        success = await database.register_player(user_id)
        
        if success:
            starting = utils.spurs_to_cogs_display(config.STARTING_BALANCE)
            embed = discord.Embed(
                title="🎉 Welcome to Gearfall Stock Exchange!",
                description=f"Your account has been created successfully.",
                color=0x57F287
            )
            embed.add_field(name="💰 Starting Balance", value=f"**{starting}**", inline=False)
            embed.add_field(
                name="📚 Getting Started",
                value=(
                    "• Use `/market` to view all stocks\n"
                    "• Use `/stock <symbol>` to trade\n"
                    "• Use `/portfolio` to view your holdings\n"
                    "• Use `/graph <symbol>` to see price history"
                ),
                inline=False
            )
            embed.set_footer(text="Trade wisely and may the markets be in your favor!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ You already have an account!",
                ephemeral=True
            )
    
    @app_commands.command(name="balance", description="View your Cog/Spur balance")
    async def balance(self, interaction: discord.Interaction):
        """View player balance."""
        user_id = interaction.user.id
        player = await database.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have an account! Use `/register` to create one.",
                ephemeral=True
            )
            return
        
        balance_str = utils.spurs_to_cogs_display(player['balance'])
        
        # Get portfolio value
        holdings = await database.get_portfolio(user_id)
        prices = await market.market.get_all_prices()
        total_value = utils.calculate_total_value(player['balance'], holdings, prices)
        total_value_str = utils.format_price(total_value)
        
        # Calculate net worth change
        net_worth_change = total_value - config.STARTING_BALANCE
        net_worth_change_pct = (net_worth_change / config.STARTING_BALANCE * 100) if config.STARTING_BALANCE > 0 else 0
        
        embed = discord.Embed(
            title="💰 Your Wallet",
            color=0xFEE75C
        )
        
        embed.add_field(name="💵 Cash Balance", value=f"**{balance_str}**", inline=True)
        embed.add_field(name="💎 Total Net Worth", value=f"**{total_value_str}**", inline=True)
        
        change_emoji = "📈" if net_worth_change >= 0 else "📉"
        change_sign = "+" if net_worth_change >= 0 else ""
        change_str = utils.format_price(abs(net_worth_change))
        embed.add_field(
            name=f"{change_emoji} Net Change",
            value=f"{change_sign}{change_str}\n({net_worth_change_pct:+.2f}%)",
            inline=True
        )
        
        embed.set_footer(text="Use /portfolio to view your holdings")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="market", description="List all team stocks and prices")
    async def market_list(self, interaction: discord.Interaction):
        """Display current market prices with mini graph."""
        await interaction.response.defer()
        
        stocks = await market.market.get_all_stocks()
        
        if not stocks:
            await interaction.followup.send(
                "❌ Market data unavailable.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📈 Gearfall Stock Exchange",
            description="Live market prices • Updates every 3 minutes",
            color=0x5865F2
        )
        
        # Calculate total market cap and biggest movers
        total_volume = 0
        biggest_gainer = None
        biggest_loser = None
        max_gain = float('-inf')
        max_loss = float('inf')
        
        for stock in stocks:
            change = stock['current_price'] - stock['starting_price']
            change_pct = (change / stock['starting_price'] * 100) if stock['starting_price'] > 0 else 0
            
            if change_pct > max_gain:
                max_gain = change_pct
                biggest_gainer = (stock['symbol'], change_pct)
            if change_pct < max_loss:
                max_loss = change_pct
                biggest_loser = (stock['symbol'], change_pct)
        
        for stock in sorted(stocks, key=lambda x: x['symbol']):
            price_str = utils.format_price(stock['current_price'])
            change = stock['current_price'] - stock['starting_price']
            change_pct = (change / stock['starting_price'] * 100) if stock['starting_price'] > 0 else 0
            
            # Price movement indicator
            if change_pct > 0:
                indicator = "📈"
                change_color = "+"
            elif change_pct < 0:
                indicator = "📉"
                change_color = ""
            else:
                indicator = "➡️"
                change_color = ""
            
            embed.add_field(
                name=f"{indicator} {stock['symbol']} - {stock['team_name']}",
                value=f"**{price_str}** ({change_color}{change_pct:.2f}%)",
                inline=True
            )
        
        # Market summary
        summary = ""
        if biggest_gainer:
            summary += f"🏆 Top Gainer: **{biggest_gainer[0]}** (+{biggest_gainer[1]:.2f}%)\n"
        if biggest_loser:
            summary += f"⚠️ Biggest Loser: **{biggest_loser[0]}** ({biggest_loser[1]:.2f}%)"
        
        if summary:
            embed.add_field(name="📊 Market Summary", value=summary, inline=False)
        
        embed.set_footer(text="Use /stock <symbol> to view details and trade • /compare to view comparison graph")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="buy", description="Buy stock shares")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, VOC)",
        shares="Number of shares to buy"
    )
    async def buy(self, interaction: discord.Interaction, symbol: str, shares: int):
        """Buy stock shares."""
        user_id = interaction.user.id
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        # Validate shares
        if shares <= 0:
            await interaction.response.send_message(
                "❌ Number of shares must be positive!",
                ephemeral=True
            )
            return
        
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
            team_config = config.TEAMS.get(symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    await interaction.response.send_message(
                        f"🚫 **Anti-Manipulation Policy**\n"
                        f"You cannot buy your own team's stock to prevent insider trading!\n\n"
                        f"Team members have advance knowledge of builds and events, "
                        f"which would give unfair trading advantages.",
                        ephemeral=True
                    )
                    return
        
        # ANTI-MANIPULATION: Check if team has active trading cooldown from admin events
        cooldown_remaining = await database.check_team_trade_cooldown(symbol)
        if cooldown_remaining and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    hours = cooldown_remaining // 3600
                    minutes = (cooldown_remaining % 3600) // 60
                    await interaction.response.send_message(
                        f"⏳ **Trading Cooldown Active**\n"
                        f"Your team cannot trade this stock for **{hours}h {minutes}m** "
                        f"after the recent admin event (build rating/heat).\n\n"
                        f"This prevents manipulation after knowing the outcome.",
                        ephemeral=True
                    )
                    return
        
        # Get current price
        price = await market.market.get_price(symbol)
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
        
        portfolio_updated = await database.update_portfolio(user_id, symbol, shares, price, is_buy=True)
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
            user_id, 'BUY', symbol, total_cost, shares, price
        )
        
        # Success message
        team_name = team_detection.get_team_name(symbol)
        price_str = utils.format_price(price)
        total_str = utils.format_price(total_cost)
        
        embed = discord.Embed(
            title="✅ Purchase Complete",
            color=discord.Color.green()
        )
        embed.add_field(name="Stock", value=f"{symbol} - {team_name}", inline=False)
        embed.add_field(name="Shares", value=f"{shares}", inline=True)
        embed.add_field(name="Price per Share", value=price_str, inline=True)
        embed.add_field(name="Total Cost", value=total_str, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="sell", description="Sell stock shares")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, VOC)",
        shares="Number of shares to sell"
    )
    async def sell(self, interaction: discord.Interaction, symbol: str, shares: int):
        """Sell stock shares."""
        user_id = interaction.user.id
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        # Validate shares
        if shares <= 0:
            await interaction.response.send_message(
                "❌ Number of shares must be positive!",
                ephemeral=True
            )
            return
        
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
            team_config = config.TEAMS.get(symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    await interaction.response.send_message(
                        f"🚫 **Anti-Manipulation Policy**\n"
                        f"You cannot sell your own team's stock to prevent insider trading!\n\n"
                        f"This prevents profiting from advance knowledge of builds and events.",
                        ephemeral=True
                    )
                    return
        
        # ANTI-MANIPULATION: Check if team has active trading cooldown from admin events
        cooldown_remaining = await database.check_team_trade_cooldown(symbol)
        if cooldown_remaining and isinstance(interaction.user, discord.Member):
            team_config = config.TEAMS.get(symbol)
            if team_config:
                team_role = discord.utils.get(interaction.user.roles, name=team_config['role_name'])
                if team_role:
                    hours = cooldown_remaining // 3600
                    minutes = (cooldown_remaining % 3600) // 60
                    await interaction.response.send_message(
                        f"⏳ **Trading Cooldown Active**\n"
                        f"Your team cannot trade this stock for **{hours}h {minutes}m** "
                        f"after the recent admin event.\n\n"
                        f"This prevents selling after knowing the outcome.",
                        ephemeral=True
                    )
                    return
        
        # Check holdings
        holding = await database.get_holding(user_id, symbol)
        if not holding or holding['shares'] < shares:
            owned = holding['shares'] if holding else 0
            await interaction.response.send_message(
                f"❌ You don't have enough shares!\nOwned: **{owned}**\nTrying to sell: **{shares}**",
                ephemeral=True
            )
            return
        
        # Get current price
        price = await market.market.get_price(symbol)
        if price is None:
            await interaction.response.send_message(
                "❌ Unable to get stock price.",
                ephemeral=True
            )
            return
        
        # Calculate total proceeds
        total_proceeds = price * shares
        
        # Execute trade
        portfolio_updated = await database.update_portfolio(user_id, symbol, shares, price, is_buy=False)
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
            user_id, 'SELL', symbol, total_proceeds, shares, price
        )
        
        # Success message
        team_name = team_detection.get_team_name(symbol)
        price_str = utils.format_price(price)
        total_str = utils.format_price(total_proceeds)
        
        embed = discord.Embed(
            title="✅ Sale Complete",
            color=discord.Color.green()
        )
        embed.add_field(name="Stock", value=f"{symbol} - {team_name}", inline=False)
        embed.add_field(name="Shares", value=f"{shares}", inline=True)
        embed.add_field(name="Price per Share", value=price_str, inline=True)
        embed.add_field(name="Total Proceeds", value=total_str, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="portfolio", description="View your holdings and profit/loss")
    async def portfolio(self, interaction: discord.Interaction):
        """View player portfolio."""
        user_id = interaction.user.id
        
        # Check if player exists
        player = await database.get_player(user_id)
        if not player:
            await interaction.response.send_message(
                "❌ You don't have an account! Use `/register` to create one.",
                ephemeral=True
            )
            return
        
        # Get portfolio
        holdings = await database.get_portfolio(user_id)
        
        if not holdings:
            balance_str = utils.format_price(player['balance'])
            await interaction.response.send_message(
                f"📊 Your portfolio is empty!\nBalance: **{balance_str}**",
                ephemeral=True
            )
            return
        
        # Get current prices
        prices = await market.market.get_all_prices()
        
        embed = discord.Embed(
            title="📊 Your Portfolio",
            color=discord.Color.blue()
        )
        
        total_pl = 0
        
        for holding in holdings:
            symbol = holding['symbol']
            shares = holding['shares']
            avg_cost = holding['avg_cost']
            current_price = prices.get(symbol, 0)
            
            team_name = team_detection.get_team_name(symbol)
            
            pl, pl_pct = utils.calculate_profit_loss(avg_cost, current_price, shares)
            total_pl += pl
            
            pl_str = utils.format_price(abs(pl))
            pl_sign = "+" if pl >= 0 else "-"
            pl_emoji = "📈" if pl >= 0 else "📉"
            
            current_value = utils.format_price(current_price * shares)
            avg_cost_str = utils.format_price(avg_cost)
            
            field_value = (
                f"Shares: **{shares}**\n"
                f"Avg Cost: **{avg_cost_str}** per share\n"
                f"Current Value: **{current_value}**\n"
                f"P&L: {pl_emoji} **{pl_sign}{pl_str}** ({pl_pct:+.2f}%)"
            )
            
            embed.add_field(
                name=f"{symbol} - {team_name}",
                value=field_value,
                inline=False
            )
        
        # Add balance and total
        balance_str = utils.format_price(player['balance'])
        total_value = utils.calculate_total_value(player['balance'], holdings, prices)
        total_value_str = utils.format_price(total_value)
        total_pl_str = utils.format_price(abs(total_pl))
        total_pl_sign = "+" if total_pl >= 0 else "-"
        
        embed.add_field(
            name="💰 Balance",
            value=balance_str,
            inline=True
        )
        embed.add_field(
            name="📈 Total Value",
            value=total_value_str,
            inline=True
        )
        embed.add_field(
            name="💹 Total P&L",
            value=f"{total_pl_sign}{total_pl_str}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="View richest players by total value")
    async def leaderboard(self, interaction: discord.Interaction):
        """View leaderboard of richest players with rankings."""
        await interaction.response.defer()
        
        # Get top players by balance
        top_players = await database.get_leaderboard(limit=15)
        
        if not top_players:
            await interaction.followup.send(
                "❌ No players registered yet!",
                ephemeral=True
            )
            return
        
        # Get current prices for portfolio calculation
        prices = await market.market.get_all_prices()
        
        embed = discord.Embed(
            title="🏆 GSC Leaderboard",
            description="Top traders by total net worth\n━━━━━━━━━━━━━━━━━━━━",
            color=0xFEE75C
        )
        
        # Calculate total values
        leaderboard_data = []
        for user_id, balance in top_players:
            portfolio = await database.get_portfolio(user_id)
            total_value = utils.calculate_total_value(balance, portfolio, prices)
            leaderboard_data.append((user_id, total_value))
        
        # Sort by total value
        leaderboard_data.sort(key=lambda x: x[1], reverse=True)
        
        # Display top 10
        leaderboard_text = ""
        for idx, (user_id, total_value) in enumerate(leaderboard_data[:10], start=1):
            try:
                user = await self.bot.fetch_user(user_id)
                username = user.display_name[:20]  # Limit length
            except:
                username = f"User {user_id}"
            
            value_str = utils.format_price(total_value)
            
            if idx == 1:
                medal = "🥇"
                username_display = f"**{username}**"
            elif idx == 2:
                medal = "🥈"
                username_display = f"**{username}**"
            elif idx == 3:
                medal = "🥉"
                username_display = f"**{username}**"
            else:
                medal = f"`#{idx}`"
                username_display = username
            
            leaderboard_text += f"{medal} {username_display}\n└ {value_str}\n"
        
        embed.description += f"\n\n{leaderboard_text}"
        
        # Add statistics
        total_registered = len(top_players)
        total_wealth = sum(v for _, v in leaderboard_data)
        avg_wealth = total_wealth // total_registered if total_registered > 0 else 0
        
        embed.add_field(
            name="📊 Market Statistics",
            value=(
                f"**Total Traders:** {total_registered}\n"
                f"**Total Wealth:** {utils.format_price(total_wealth)}\n"
                f"**Average Net Worth:** {utils.format_price(avg_wealth)}"
            ),
            inline=False
        )
        
        embed.set_footer(text="Rankings update in real-time • Use /portfolio to track your progress")
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(UserCommands(bot))
