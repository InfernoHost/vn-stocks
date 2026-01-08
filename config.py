"""Configuration for the Discord economy bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', 0))

# Market Updates Channel
MARKET_UPDATES_CHANNEL_ID = int(os.getenv('MARKET_UPDATES_CHANNEL_ID', 0))
MARKET_UPDATES_INTERVAL = 900  # 15 minutes (in seconds)

# Currency Configuration
SPURS_PER_COG = 64

# Starting Balance (in Spurs)
STARTING_BALANCE = 10 * SPURS_PER_COG  # 10 Cogs

# Market Configuration
MARKET_UPDATE_INTERVAL = 180  # 3 minutes (in seconds)
PRICE_HISTORY_MAX = 10000  # Maximum price history entries per stock

# Team Configuration
TEAMS = {
    'STMP': {
        'name': 'Team Steampire',
        'symbol': 'STMP',
        'starting_price': 1 * SPURS_PER_COG,  # 1 Cog in Spurs
        'volatility': 0.02,  # 2% volatility
        'role_name': 'Team Steampire'
    },
    'VOC': {
        'name': 'Team VOC',
        'symbol': 'VOC',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team VOC'
    },
    'CRAV': {
        'name': 'Team Crava',
        'symbol': 'CRAV',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team Crava'
    },
    'ROSE': {
        'name': 'Team Rose',
        'symbol': 'ROSE',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team Rose'
    },
    'VIOL': {
        'name': 'Team Violet',
        'symbol': 'VIOL',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team Violet'
    },
    'POT': {
        'name': 'Team Potchi',
        'symbol': 'POT',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team Potchi'
    },
    'HORZ': {
        'name': 'Team New Horizon',
        'symbol': 'HORZ',
        'starting_price': 1 * SPURS_PER_COG,
        'volatility': 0.02,
        'role_name': 'Team New Horizon'
    }
}

# Team Tag Mapping (case-insensitive)
TEAM_TAGS = {
    'STEAMPIRE': 'STMP',
    'STMP': 'STMP',
    'CRAVA': 'CRAV',
    'CRAV': 'CRAV',
    'ROSE': 'ROSE',
    'VOC': 'VOC',
    'POTCHI': 'POT',
    'KOS': 'POT',
    'CRACKHEAD': 'POT',
    'TEMP': 'VIOL',
    'VIOLET': 'VIOL',
    '[[L]]': 'VIOL',
    'HORIZON': 'HORZ',
    'HORZ': 'HORZ',
    'NEW HORIZON': 'HORZ',
    'NH': 'HORZ'
}

# Message Influence Configuration
MESSAGE_COOLDOWN = 60  # Seconds between messages that count for market influence
ACTIVITY_DECAY = 0.95  # Activity score decay per market update
ACTIVITY_IMPACT = 0.001  # Impact of activity on price movement

# Anti-Manipulation Configuration
PREVENT_OWN_TEAM_TRADING = True  # Block team members from trading their own team's stock
ADMIN_EVENT_COOLDOWN = 3600  # 1 hour cooldown after /ratebuild or /heat (in seconds)
MAX_OWN_TEAM_SHARES = 5  # Max shares a team member can hold of their own team (if not fully blocked)

# Database Configuration
DB_PATH = 'data/economy.db'

# Market Data Configuration
MARKET_DATA_DIR = 'data/stocks'

# Graph Configuration
GRAPH_DIR = 'data/graphs'
GRAPH_WIDTH = 12
GRAPH_HEIGHT = 6
GRAPH_DPI = 100

# Trading and Market Constants
MOMENTUM_PERSISTENCE_FACTOR = 0.3  # Momentum carries 30% to next update
MOMENTUM_IMPACT_FACTOR = 0.3  # Momentum contributes 30% to price change
MEAN_REVERSION_STRENGTH = 0.01  # 1% pull towards starting price
MAX_VOLATILITY_MULTIPLIER = 6  # Maximum change is 6x volatility
HEAT_BUFF_PERCENTAGE = 0.25  # 25% price increase for HEAT command
RATING_MAX_IMPACT = 0.15  # Build rating can cause ±15% price change
