"""Admin commands for the economy bot."""
import discord
from discord import app_commands
from discord.ext import commands
import database
import market
import team_detection
import utils
import config


class AdminCommands(commands.Cog):
    """Admin-only commands for managing the economy."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(interaction: discord.Interaction) -> bool:
        """Check if user has admin role."""
        if not isinstance(interaction.user, discord.Member):
            return False
        
        admin_role = discord.utils.get(interaction.user.roles, id=config.ADMIN_ROLE_ID)
        return admin_role is not None
    
    @app_commands.command(name="give", description="[Admin] Give Cogs to a user")
    @app_commands.describe(
        user="The user to give Cogs to",
        cogs="Number of Cogs to give"
    )
    @app_commands.check(is_admin)
    async def give(self, interaction: discord.Interaction, user: discord.User, cogs: int):
        """Give Cogs to a user."""
        if cogs <= 0:
            await interaction.response.send_message(
                "❌ Amount must be positive!",
                ephemeral=True
            )
            return
        
        # Check if target player exists
        player = await database.get_player(user.id)
        if not player:
            await interaction.response.send_message(
                f"❌ {user.display_name} doesn't have an account!",
                ephemeral=True
            )
            return
        
        # Convert cogs to spurs
        spurs = utils.cogs_to_spurs(cogs)
        
        # Update balance
        success = await database.update_balance(user.id, spurs)
        if not success:
            await interaction.response.send_message(
                "❌ Failed to update balance.",
                ephemeral=True
            )
            return
        
        # Log admin action
        await database.log_admin_action(
            interaction.user.id,
            'GIVE',
            user.id,
            f"Gave {cogs} Cogs ({spurs} Spurs)"
        )
        
        # Log transaction
        await database.log_transaction(
            user.id, 'ADMIN_GIVE', amount=spurs
        )
        
        amount_str = utils.spurs_to_cogs_display(spurs)
        await interaction.response.send_message(
            f"✅ Gave **{amount_str}** to {user.mention}",
            ephemeral=True
        )
    
    @app_commands.command(name="take", description="[Admin] Take Cogs from a user")
    @app_commands.describe(
        user="The user to take Cogs from",
        cogs="Number of Cogs to take"
    )
    @app_commands.check(is_admin)
    async def take(self, interaction: discord.Interaction, user: discord.User, cogs: int):
        """Take Cogs from a user."""
        if cogs <= 0:
            await interaction.response.send_message(
                "❌ Amount must be positive!",
                ephemeral=True
            )
            return
        
        # Check if target player exists
        player = await database.get_player(user.id)
        if not player:
            await interaction.response.send_message(
                f"❌ {user.display_name} doesn't have an account!",
                ephemeral=True
            )
            return
        
        # Convert cogs to spurs
        spurs = utils.cogs_to_spurs(cogs)
        
        # Update balance
        success = await database.update_balance(user.id, -spurs)
        if not success:
            current_balance = utils.format_price(player['balance'])
            await interaction.response.send_message(
                f"❌ Insufficient funds! {user.display_name} has: **{current_balance}**",
                ephemeral=True
            )
            return
        
        # Log admin action
        await database.log_admin_action(
            interaction.user.id,
            'TAKE',
            user.id,
            f"Took {cogs} Cogs ({spurs} Spurs)"
        )
        
        # Log transaction
        await database.log_transaction(
            user.id, 'ADMIN_TAKE', amount=spurs
        )
        
        amount_str = utils.spurs_to_cogs_display(spurs)
        await interaction.response.send_message(
            f"✅ Took **{amount_str}** from {user.mention}",
            ephemeral=True
        )
    
    @app_commands.command(name="setprice", description="[Admin] Set stock price")
    @app_commands.describe(
        symbol="Stock symbol (e.g., STMP, VOC)",
        price="New price in Cogs"
    )
    @app_commands.check(is_admin)
    async def setprice(self, interaction: discord.Interaction, symbol: str, price: int):
        """Set stock price manually."""
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        if price <= 0:
            await interaction.response.send_message(
                "❌ Price must be positive!",
                ephemeral=True
            )
            return
        
        # Convert price to spurs
        price_spurs = utils.cogs_to_spurs(price)
        
        # Update price
        await market.market.update_price(symbol, price_spurs)
        
        # Log admin action
        team_name = team_detection.get_team_name(symbol)
        await database.log_admin_action(
            interaction.user.id,
            'SETPRICE',
            details=f"Set {symbol} ({team_name}) price to {price} Cogs ({price_spurs} Spurs)"
        )
        
        price_str = utils.format_price(price_spurs)
        await interaction.response.send_message(
            f"✅ Set **{symbol}** ({team_name}) price to **{price_str}**",
            ephemeral=True
        )
    
    @app_commands.command(name="resetmarket", description="[Admin] Reset all stock prices to starting values")
    @app_commands.check(is_admin)
    async def resetmarket(self, interaction: discord.Interaction):
        """Reset all stock prices to starting values."""
        await interaction.response.defer(ephemeral=True)
        
        # Reset prices
        await market.market.reset_prices()
        
        # Reset activity scores
        market.market.reset_activity()
        
        # Log admin action
        await database.log_admin_action(
            interaction.user.id,
            'RESETMARKET',
            details="Reset all stock prices to starting values"
        )
        
        await interaction.followup.send(
            "✅ Market reset! All stock prices have been reset to their starting values.",
            ephemeral=True
        )
    
    @app_commands.command(name="ratebuild", description="[Admin] Rate a team's build out of 10")
    @app_commands.describe(
        symbol="Team symbol (e.g., STMP, VOC)",
        rating="Rating out of 10 (1-10)"
    )
    @app_commands.check(is_admin)
    async def ratebuild(self, interaction: discord.Interaction, symbol: str, rating: int):
        """Rate a team's build, affecting their stock price."""
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        # Validate rating
        if rating < 1 or rating > 10:
            await interaction.response.send_message(
                "❌ Rating must be between 1 and 10!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get current price
        current_price = await market.market.get_price(symbol)
        if current_price is None:
            await interaction.followup.send(
                "❌ Unable to get stock price.",
                ephemeral=True
            )
            return
        
        # Calculate price change based on rating
        # Rating 5 = neutral, above 5 = positive, below 5 = negative
        rating_impact = (rating - 5) / 5  # Range: -0.8 to +1.0
        price_change_pct = rating_impact * 0.15  # Max ±15% change
        
        price_change = int(current_price * price_change_pct)
        new_price = max(1, current_price + price_change)  # Ensure price stays positive
        
        # Update price
        await market.market.update_price(symbol, new_price)
        
        # Apply trading cooldown to prevent team members from manipulating after rating
        await database.set_team_trade_cooldown(symbol, config.ADMIN_EVENT_COOLDOWN)
        
        # Log admin action
        team_name = team_detection.get_team_name(symbol)
        await database.log_admin_action(
            interaction.user.id,
            'RATEBUILD',
            details=f"Rated {symbol} ({team_name}) build: {rating}/10 (Price change: {price_change_pct*100:+.1f}%)"
        )
        
        # Create embed for public announcement
        team_config = config.TEAMS.get(symbol)
        team_role_name = team_config['role_name'] if team_config else None
        
        # Try to find and mention the team role
        team_role = None
        if team_role_name and interaction.guild:
            team_role = discord.utils.get(interaction.guild.roles, name=team_role_name)
        
        # Rating emoji
        if rating >= 9:
            rating_emoji = "🌟🌟🌟"
            rating_text = "Outstanding!"
        elif rating >= 7:
            rating_emoji = "⭐⭐⭐"
            rating_text = "Excellent!"
        elif rating >= 5:
            rating_emoji = "⭐⭐"
            rating_text = "Good!"
        elif rating >= 3:
            rating_emoji = "⭐"
            rating_text = "Decent"
        else:
            rating_emoji = "💩"
            rating_text = "Needs Work"
        
        embed = discord.Embed(
            title=f"🏗️ Build Rating: {symbol} - {team_name}",
            description=f"{rating_emoji} **{rating}/10** - {rating_text}",
            color=0x57F287 if rating >= 6 else 0xFEE75C if rating >= 4 else 0xED4245
        )
        
        # Show price impact
        price_str = utils.format_price(new_price)
        change_emoji = "📈" if price_change >= 0 else "📉"
        change_sign = "+" if price_change >= 0 else ""
        change_str = utils.format_price(abs(price_change))
        
        embed.add_field(
            name="💰 Stock Impact",
            value=f"**{price_str}** ({change_emoji} {change_sign}{change_str} / {price_change_pct*100:+.1f}%)",
            inline=False
        )
        
        embed.set_footer(text=f"Rated by {interaction.user.display_name}")
        
        # Send public message with team mention
        if team_role:
            await interaction.followup.send(
                content=f"{team_role.mention} 🎨 Your build has been rated!",
                embed=embed
            )
        else:
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="heat", description="[Admin] Apply HEAT buff to a team's stock!")
    @app_commands.describe(symbol="Team symbol (e.g., STMP, VOC)")
    @app_commands.check(is_admin)
    async def heat(self, interaction: discord.Interaction, symbol: str):
        """Apply a HEAT buff to a team, giving them a significant stock boost."""
        symbol = team_detection.normalize_symbol(symbol)
        
        # Validate symbol
        if not team_detection.validate_symbol(symbol):
            await interaction.response.send_message(
                f"❌ Invalid stock symbol: **{symbol}**",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get current price
        current_price = await market.market.get_price(symbol)
        if current_price is None:
            await interaction.followup.send(
                "❌ Unable to get stock price.",
                ephemeral=True
            )
            return
        
        # Apply HEAT buff: 25% price increase
        heat_buff = 0.25
        price_increase = int(current_price * heat_buff)
        new_price = current_price + price_increase
        
        # Update price
        await market.market.update_price(symbol, new_price)
        
        # Add extra activity boost for momentum
        market.market.increment_activity(symbol)
        market.market.increment_activity(symbol)
        market.market.increment_activity(symbol)
        
        # Apply trading cooldown to prevent team members from manipulating after HEAT
        await database.set_team_trade_cooldown(symbol, config.ADMIN_EVENT_COOLDOWN)
        
        # Log admin action
        team_name = team_detection.get_team_name(symbol)
        await database.log_admin_action(
            interaction.user.id,
            'HEAT',
            details=f"Applied HEAT buff to {symbol} ({team_name}) - Price: +{heat_buff*100:.0f}%"
        )
        
        # Get team role for mention
        team_config = config.TEAMS.get(symbol)
        team_role_name = team_config['role_name'] if team_config else None
        
        team_role = None
        if team_role_name and interaction.guild:
            team_role = discord.utils.get(interaction.guild.roles, name=team_role_name)
        
        # Create epic announcement embed
        embed = discord.Embed(
            title="🔥🔥🔥 ADMIN HEAT! 🔥🔥🔥",
            description=f"**{symbol} - {team_name}** is ON FIRE!",
            color=0xED4245
        )
        
        price_str = utils.format_price(new_price)
        increase_str = utils.format_price(price_increase)
        
        embed.add_field(
            name="🚀 STOCK BUFF APPLIED",
            value=f"**+{increase_str}** (+{heat_buff*100:.0f}%)\n**New Price: {price_str}**",
            inline=False
        )
        
        embed.add_field(
            name="🎊 CONGRATULATIONS!",
            value="Your stock is soaring! 📈",
            inline=False
        )
        
        embed.set_footer(text=f"Heat applied by {interaction.user.display_name}")
        
        # Send epic announcement
        if team_role:
            await interaction.followup.send(
                content=f"{team_role.mention} 🔥🔥🔥 **ADMIN HEAT!!!** 🔥🔥🔥\n**APPLYING STOCK BUFF** 🎊 **CONGRATS** 🎉🎊🎉",
                embed=embed
            )
        else:
            await interaction.followup.send(
                content=f"🔥🔥🔥 **ADMIN HEAT!!!** 🔥🔥🔥\n**{symbol} - {team_name}**\n**APPLYING STOCK BUFF** 🎊 **CONGRATS** 🎉🎊🎉",
                embed=embed
            )
    
    @app_commands.command(name="marketupdate", description="[Admin] Manually trigger a market update broadcast")
    @app_commands.check(is_admin)
    async def marketupdate(self, interaction: discord.Interaction):
        """Manually trigger a market update broadcast."""
        await interaction.response.defer(ephemeral=True)
        
        # Check if broadcaster exists
        if not hasattr(self.bot, 'broadcaster') or not self.bot.broadcaster:
            await interaction.followup.send(
                "❌ Market updates broadcaster is not running!",
                ephemeral=True
            )
            return
        
        # Trigger manual update
        try:
            await self.bot.broadcaster.send_market_update()
            await interaction.followup.send(
                "✅ Market update sent successfully!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to send market update: {str(e)}",
                ephemeral=True
            )
    
    @give.error
    @take.error
    @setprice.error
    @resetmarket.error
    @ratebuild.error
    @heat.error
    @marketupdate.error
    async def admin_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors for admin commands."""
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(error)}",
                ephemeral=True
            )


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(AdminCommands(bot))
