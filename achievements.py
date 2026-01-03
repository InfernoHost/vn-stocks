"""Achievement system for tracking milestones."""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import database


# Achievement definitions
ACHIEVEMENTS = {
    'first_trade': {
        'name': 'First Trade',
        'description': 'Made your first trade',
        'emoji': '🎯',
        'rarity': 'Common'
    },
    'millionaire': {
        'name': 'Millionaire',
        'description': 'Reached 1 million Spurs total value',
        'emoji': '💰',
        'rarity': 'Rare'
    },
    'diamond_hands': {
        'name': 'Diamond Hands',
        'description': 'Held a stock for 7+ days',
        'emoji': '💎',
        'rarity': 'Uncommon'
    },
    'day_trader': {
        'name': 'Day Trader',
        'description': 'Made 10+ trades in one day',
        'emoji': '📊',
        'rarity': 'Uncommon'
    },
    'diversified': {
        'name': 'Diversified',
        'description': 'Own stocks in all 6 teams',
        'emoji': '🌈',
        'rarity': 'Rare'
    },
    'whale': {
        'name': 'Whale',
        'description': 'Made a single trade worth 100k+ Cogs',
        'emoji': '🐋',
        'rarity': 'Epic'
    },
    'perfect_timing': {
        'name': 'Perfect Timing',
        'description': 'Sold a stock for 50%+ profit',
        'emoji': '⏰',
        'rarity': 'Rare'
    },
    'high_roller': {
        'name': 'High Roller',
        'description': 'Own 1000+ shares of a single stock',
        'emoji': '🎰',
        'rarity': 'Epic'
    },
    'early_bird': {
        'name': 'Early Bird',
        'description': 'Bought a stock at its all-time low',
        'emoji': '🐦',
        'rarity': 'Legendary'
    },
    'market_master': {
        'name': 'Market Master',
        'description': 'Unlocked all other achievements',
        'emoji': '👑',
        'rarity': 'Legendary'
    }
}


async def check_achievement(user_id: int, achievement_id: str) -> bool:
    """Check if user has unlocked an achievement."""
    async with database.get_db() as db:
        async with db.execute(
            "SELECT 1 FROM achievements WHERE user_id = ? AND achievement_id = ?",
            (user_id, achievement_id)
        ) as cursor:
            return await cursor.fetchone() is not None


async def unlock_achievement(user_id: int, achievement_id: str) -> bool:
    """Unlock an achievement for a user. Returns True if newly unlocked."""
    # Check if already unlocked
    if await check_achievement(user_id, achievement_id):
        return False
    
    # Unlock
    async with database.get_db() as db:
        await db.execute(
            """INSERT INTO achievements (user_id, achievement_id, unlocked_at)
               VALUES (?, ?, datetime('now'))""",
            (user_id, achievement_id)
        )
        await db.commit()
    
    # Check for Market Master
    if achievement_id != 'market_master':
        unlocked_count = 0
        for ach_id in ACHIEVEMENTS.keys():
            if ach_id != 'market_master' and await check_achievement(user_id, ach_id):
                unlocked_count += 1
        
        # If all other achievements unlocked, unlock Market Master
        if unlocked_count == len(ACHIEVEMENTS) - 1:
            await unlock_achievement(user_id, 'market_master')
    
    return True


async def check_and_unlock_achievements(user_id: int, event_type: str, **kwargs):
    """Check and unlock relevant achievements based on an event."""
    newly_unlocked = []
    
    if event_type == 'trade':
        # First Trade
        if not await check_achievement(user_id, 'first_trade'):
            if await unlock_achievement(user_id, 'first_trade'):
                newly_unlocked.append('first_trade')
        
        # Whale (100k+ Cogs trade)
        trade_value = kwargs.get('trade_value', 0)
        if trade_value >= 100_000 * 64:  # 100k Cogs in Spurs
            if await unlock_achievement(user_id, 'whale'):
                newly_unlocked.append('whale')
        
        # Perfect Timing (50%+ profit)
        profit_pct = kwargs.get('profit_pct', 0)
        if profit_pct >= 50:
            if await unlock_achievement(user_id, 'perfect_timing'):
                newly_unlocked.append('perfect_timing')
    
    elif event_type == 'portfolio_check':
        # Millionaire
        total_value = kwargs.get('total_value', 0)
        if total_value >= 1_000_000:  # 1M Spurs
            if await unlock_achievement(user_id, 'millionaire'):
                newly_unlocked.append('millionaire')
        
        # Diversified (own all 6 stocks)
        portfolio = kwargs.get('portfolio', [])
        unique_symbols = set(p['symbol'] for p in portfolio)
        if len(unique_symbols) >= 6:
            if await unlock_achievement(user_id, 'diversified'):
                newly_unlocked.append('diversified')
        
        # High Roller (1000+ shares)
        for holding in portfolio:
            if holding['shares'] >= 1000:
                if await unlock_achievement(user_id, 'high_roller'):
                    newly_unlocked.append('high_roller')
                break
    
    return newly_unlocked


class AchievementCommands(commands.Cog):
    """Commands for viewing achievements."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="achievements", description="View your unlocked achievements")
    async def achievements(self, interaction: discord.Interaction):
        """View achievements."""
        async with database.get_db() as db:
            async with db.execute(
                """SELECT achievement_id, unlocked_at FROM achievements
                   WHERE user_id = ?
                   ORDER BY unlocked_at DESC""",
                (interaction.user.id,)
            ) as cursor:
                unlocked = await cursor.fetchall()
        
        unlocked_ids = {ach[0] for ach in unlocked}
        
        embed = discord.Embed(
            title=f"🏆 {interaction.user.display_name}'s Achievements",
            description=f"Unlocked {len(unlocked)}/{len(ACHIEVEMENTS)} achievements",
            color=discord.Color.gold()
        )
        
        # Rarity order
        rarity_order = {'Common': 0, 'Uncommon': 1, 'Rare': 2, 'Epic': 3, 'Legendary': 4}
        
        # Group by rarity
        by_rarity = {}
        for ach_id, ach in ACHIEVEMENTS.items():
            rarity = ach['rarity']
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append((ach_id, ach))
        
        # Display by rarity
        for rarity in sorted(by_rarity.keys(), key=lambda r: rarity_order[r]):
            achievements_list = by_rarity[rarity]
            
            text = ""
            for ach_id, ach in achievements_list:
                if ach_id in unlocked_ids:
                    text += f"{ach['emoji']} **{ach['name']}**\n"
                    text += f"  _{ach['description']}_\n"
                else:
                    text += f"🔒 **???**\n"
                    text += f"  _{ach['description']}_\n"
            
            if text:
                embed.add_field(name=f"{rarity} Achievements", value=text, inline=False)
        
        # Progress bar
        progress = len(unlocked) / len(ACHIEVEMENTS)
        bar_length = 10
        filled = int(progress * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        embed.set_footer(text=f"Progress: {bar} {progress*100:.0f}%")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(AchievementCommands(bot))
