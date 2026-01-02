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
            'commands_info'
        ]
    
    async def setup_hook(self):
        """Initialize database, market data, and load commands."""
        print("Initializing database...")
        await database.init_db()
        
        # Initialize market data
        print("Initializing market data...")
        await market.market.initialize()
        
        # Load cogs
        print("Loading commands...")
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"  Loaded: {ext}")
            except Exception as e:
                print(f"  Failed to load {ext}: {e}", file=sys.stderr)
        
        # Sync commands to guild
        print("Syncing commands...")
        try:
            if config.GUILD_ID:
                guild = discord.Object(id=config.GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"Synced commands to guild {config.GUILD_ID}")
            else:
                await self.tree.sync()
                print("Synced commands globally")
        except Exception as e:
            print(f"Failed to sync commands: {e}", file=sys.stderr)
    
    async def on_ready(self):
        """Start background tasks once bot is connected."""
        print(f'\n{self.user} is now online!')
        print(f'Bot ID: {self.user.id}')
        print(f'Guilds: {len(self.guilds)}')
        print('---')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="📈 Gearfall Stock Exchange"
            )
        )
        
        # Start market simulator
        print("Starting market simulator...")
        market_simulator.simulator.start()
        print("Market simulator started!")
        
        # Start market updates broadcaster
        if config.MARKET_UPDATES_CHANNEL_ID:
            print("Starting market updates broadcaster...")
            self.broadcaster = market_updates.initialize_broadcaster(self)
            self.broadcaster.start()
            print(f"Broadcasting market updates to channel {config.MARKET_UPDATES_CHANNEL_ID}")
    
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
        print("Shutting down...")
        market_simulator.simulator.stop()
        if hasattr(self, 'broadcaster') and self.broadcaster:
            self.broadcaster.stop()
        await super().close()


def main():
    """Main entry point."""
    # Check configuration
    if not config.DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not set in .env file!", file=sys.stderr)
        print("Create a .env file from .env.example and add your bot token.", file=sys.stderr)
        sys.exit(1)
    
    if not config.GUILD_ID:
        print("WARNING: GUILD_ID not set in .env file.", file=sys.stderr)
        print("Commands will sync globally (takes up to 1 hour).", file=sys.stderr)
    
    if not config.ADMIN_ROLE_ID:
        print("WARNING: ADMIN_ROLE_ID not set in .env file.", file=sys.stderr)
        print("Admin commands will not work until this is configured.", file=sys.stderr)
    
    # Create and run bot
    bot = EconomyBot()
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
