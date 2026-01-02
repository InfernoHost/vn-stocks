"""Market updates broadcaster - sends periodic price updates to a channel."""
import discord
from discord.ext import tasks
from datetime import datetime
import market
import team_detection
import utils
import config


class MarketUpdatesBroadcaster:
    """Handles periodic market update broadcasts."""
    
    def __init__(self, bot):
        self.bot = bot
        self.running = False
        self.previous_prices = {}
        self.update_count = 0
    
    def start(self):
        """Start the market updates broadcast loop."""
        if not self.running:
            self.market_updates_loop.start()
            self.running = True
    
    def stop(self):
        """Stop the market updates broadcast loop."""
        if self.running:
            self.market_updates_loop.cancel()
            self.running = False
    
    @tasks.loop(seconds=config.MARKET_UPDATES_INTERVAL)
    async def market_updates_loop(self):
        """Periodic market updates broadcast."""
        await self.send_market_update()
    
    async def send_market_update(self):
        """Send market update to the designated channel."""
        if not config.MARKET_UPDATES_CHANNEL_ID:
            return
        
        try:
            channel = self.bot.get_channel(config.MARKET_UPDATES_CHANNEL_ID)
            if not channel:
                print(f"Market updates channel {config.MARKET_UPDATES_CHANNEL_ID} not found")
                return
            
            # Get all stocks
            stocks = await market.market.get_all_stocks()
            if not stocks:
                return
            
            self.update_count += 1
            
            # Create embed
            embed = discord.Embed(
                title="📊 GSC Market Update",
                description=f"Live Stock Prices • Update #{self.update_count}",
                color=0x5865F2,
                timestamp=datetime.utcnow()
            )
            
            # Track market statistics
            total_market_cap = 0
            biggest_mover = None
            max_move = 0
            movers_up = 0
            movers_down = 0
            
            # Process each stock
            for stock in sorted(stocks, key=lambda x: x['symbol']):
                symbol = stock['symbol']
                team_name = stock['team_name']
                current_price = stock['current_price']
                starting_price = stock['starting_price']
                volatility = stock['volatility']
                
                # Calculate change from start
                change_from_start = current_price - starting_price
                change_pct = (change_from_start / starting_price * 100) if starting_price > 0 else 0
                
                # Calculate change from last update
                previous_price = self.previous_prices.get(symbol, starting_price)
                recent_change = current_price - previous_price
                recent_change_pct = (recent_change / previous_price * 100) if previous_price > 0 else 0
                
                # Update previous prices
                self.previous_prices[symbol] = current_price
                
                # Track biggest mover
                if abs(recent_change_pct) > max_move:
                    max_move = abs(recent_change_pct)
                    biggest_mover = (symbol, recent_change_pct)
                
                # Count movers
                if recent_change > 0:
                    movers_up += 1
                elif recent_change < 0:
                    movers_down += 1
                
                # Get activity level
                activity_score = market.market.get_activity_score(symbol)
                if activity_score > 20:
                    activity_emoji = "🔥"
                    activity_text = "High"
                elif activity_score > 5:
                    activity_emoji = "📊"
                    activity_text = "Moderate"
                else:
                    activity_emoji = "💤"
                    activity_text = "Low"
                
                # Movement indicators
                if recent_change > 0:
                    trend_emoji = "📈"
                    trend_color = "+"
                elif recent_change < 0:
                    trend_emoji = "📉"
                    trend_color = ""
                else:
                    trend_emoji = "➡️"
                    trend_color = ""
                
                # All-time performance indicator
                if change_pct > 0:
                    performance_emoji = "🟢"
                elif change_pct < 0:
                    performance_emoji = "🔴"
                else:
                    performance_emoji = "⚪"
                
                # Format price
                price_str = utils.format_price(current_price)
                
                # Get recent high/low from history
                history = stock.get('price_history', [])
                if len(history) >= 10:
                    recent_prices = [h['price'] for h in history[-10:]]
                    high_24h = max(recent_prices)
                    low_24h = min(recent_prices)
                    range_str = f"Range: {utils.format_price(low_24h)} - {utils.format_price(high_24h)}"
                else:
                    range_str = "Building history..."
                
                field_value = (
                    f"**{price_str}** {trend_emoji} {trend_color}{abs(recent_change_pct):.2f}% (recent)\n"
                    f"{performance_emoji} All-Time: {change_pct:+.2f}%\n"
                    f"{activity_emoji} Activity: {activity_text}\n"
                    f"📊 Volatility: {volatility*100:.1f}%\n"
                    f"📉📈 {range_str}"
                )
                
                embed.add_field(
                    name=f"{symbol} - {team_name}",
                    value=field_value,
                    inline=True
                )
            
            # Add market summary
            summary_text = ""
            if biggest_mover:
                move_emoji = "📈" if biggest_mover[1] > 0 else "📉"
                summary_text += f"{move_emoji} **Biggest Mover:** {biggest_mover[0]} ({biggest_mover[1]:+.2f}%)\n"
            
            summary_text += f"📊 **Market Sentiment:** {movers_up} up, {movers_down} down\n"
            summary_text += f"⏰ **Next Update:** <t:{int((datetime.utcnow().timestamp() + config.MARKET_UPDATES_INTERVAL))}:R>"
            
            embed.add_field(
                name="📈 Market Summary",
                value=summary_text,
                inline=False
            )
            
            embed.set_footer(
                text="GSC - Gearfall Stock Exchange • Prices update every 3 minutes",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            # Send the update
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error sending market update: {e}")
    
    @market_updates_loop.before_loop
    async def before_market_updates(self):
        """Wait for bot to be ready before starting broadcasts."""
        await self.bot.wait_until_ready()


# Global broadcaster instance
broadcaster = None

def initialize_broadcaster(bot):
    """Initialize the market updates broadcaster."""
    global broadcaster
    broadcaster = MarketUpdatesBroadcaster(bot)
    return broadcaster
