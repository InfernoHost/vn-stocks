"""GSC - Gearfall Stock Exchange - Discord economy bot for Minecraft server."""
import discord
from discord.ext import commands
import asyncio
import sys
import config
import database
import market
import team_detection
import market_simulator
import market_updates
from logger import logger


class EconomyBot(commands.Bot):
    """Main bot instance. Handles events and manages background tasks."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',  # Required by discord.py but unused (slash commands only)
            intents=intents
        )
        
        self.initial_extensions = [
            'commands_user',
            'commands_admin',
            'commands_graph',
            'commands_stock',
            'commands_info',
            'commands_limit',
            'commands_portfolio',
            'commands_alerts',
            'commands_history',
            'commands_watchlist',
            'achievements',
            'commands_candlestick'
        ]
    
    async def setup_hook(self):
        """Initialize database, market data, and load commands."""
        logger.info("Initializing database...")
        await database.init_db()
        
        # Initialize market data
        logger.info("Initializing market data...")
        await market.market.initialize()
        
        # Register persistent views for live graphs
        from live_graphs import LiveGraphView
        self.add_view(LiveGraphView())
        logger.info("Registered persistent views")
        
        # Load cogs
        logger.info("Loading commands...")
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"  Loaded: {ext}")
            except Exception as e:
                logger.error(f"  Failed to load {ext}: {e}")
        
        # Sync commands to guild
        logger.info("Syncing commands...")
        try:
            if config.GUILD_ID:
                guild = discord.Object(id=config.GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"Synced commands to guild {config.GUILD_ID}")
            else:
                await self.tree.sync()
                logger.info("Synced commands globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Start background tasks once bot is connected."""
        logger.info(f'\n{self.user} is now online!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Guilds: {len(self.guilds)}')
        logger.info('---')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="📈 Gearfall Stock Exchange"
            )
        )
        
        # Start market simulator
        logger.info("Starting market simulator...")
        market_simulator.simulator.start()
        logger.info("Market simulator started!")
        
        # Start market updates broadcaster
        if config.MARKET_UPDATES_CHANNEL_ID:
            logger.info("Starting market updates broadcaster...")
            self.broadcaster = market_updates.initialize_broadcaster(self)
            self.broadcaster.start()
            logger.info(f"Broadcasting market updates to channel {config.MARKET_UPDATES_CHANNEL_ID}")
        
        # Start price alerts checker
        logger.info("Starting price alerts checker...")
        from price_alerts import check_and_trigger_alerts
        
        async def alert_loop():
            while True:
                try:
                    await check_and_trigger_alerts(self)
                except Exception as e:
                    logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(60)  # Check every minute
        
        self.loop.create_task(alert_loop())
        logger.info("Price alerts checker started!")
    
    async def on_message(self, message: discord.Message):
        """Process messages for team activity scoring."""
        # Ignore DMs
        if not message.guild:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check message cooldown
        user_id = message.author.id
        can_influence = await database.check_message_cooldown(user_id, config.MESSAGE_COOLDOWN)
        
        if not can_influence:
            return
        
        # Detect team from message
        team_symbol = team_detection.detect_team_from_message(message)
        
        if team_symbol:
            # Increment activity score for the team
            market.market.increment_activity(team_symbol)
            
            # Optional: Log for debugging
            # print(f"Message from {message.author} attributed to {team_symbol}")
    
    async def close(self):
        """Cleanup when bot is shutting down."""
        logger.info("Shutting down...")
        market_simulator.simulator.stop()
        if hasattr(self, 'broadcaster') and self.broadcaster:
            self.broadcaster.stop()
        await super().close()


def main():
    """Main entry point."""
    # Check configuration
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in .env file!")
        logger.error("Create a .env file from .env.example and add your bot token.")
        sys.exit(1)
    
    if not config.GUILD_ID:
        logger.warning("GUILD_ID not set in .env file.")
        logger.warning("Commands will sync globally (takes up to 1 hour).")
    
    if not config.ADMIN_ROLE_ID:
        logger.warning("ADMIN_ROLE_ID not set in .env file.")
        logger.warning("Admin commands will not work until this is configured.")
    
    # Create and run bot
    bot = EconomyBot()
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
