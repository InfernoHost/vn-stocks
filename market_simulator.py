"""Market simulation - background task for updating prices."""
import random
import math
from discord.ext import tasks
import market
import config


class MarketSimulator:
    """Handles periodic price updates with volatility and momentum."""
    
    def __init__(self):
        self.running = False
        self.momentum = {symbol: 0.0 for symbol in config.TEAMS.keys()}
        self.trend_strength = {symbol: 0.0 for symbol in config.TEAMS.keys()}
    
    def start(self):
        """Start the market update loop."""
        if not self.running:
            self.market_update_loop.start()
            self.running = True
    
    def stop(self):
        """Stop the market update loop."""
        if self.running:
            self.market_update_loop.cancel()
            self.running = False
    
    @tasks.loop(seconds=config.MARKET_UPDATE_INTERVAL)
    async def market_update_loop(self):
        """Update prices every few minutes."""
        await self.update_market_prices()
        
        # Check and execute limit orders
        from limit_orders import check_and_execute_orders
        executed = await check_and_execute_orders()
        
        if executed:
            import logging
            logging.getLogger(__name__).info(f"Executed {len(executed)} limit orders")
    
    async def update_market_prices(self):
        """Calculate new prices based on activity and volatility."""
        for symbol, team in config.TEAMS.items():
            current_price = await market.market.get_price(symbol)
            if current_price is None:
                continue
            
            # Get activity score
            activity_score = market.market.get_activity_score(symbol)
            
            # Calculate new price
            new_price = self._calculate_new_price(
                current_price,
                team['volatility'],
                activity_score,
                symbol
            )
            
            # Ensure price doesn't go below 1 Spur
            new_price = max(1, new_price)
            
            # Update price in market data
            await market.market.update_price(symbol, new_price)
        
        # Decay activity scores
        market.market.decay_activity()
    
    def _calculate_new_price(self, current_price: int, volatility: float, activity_score: float, symbol: str) -> int:
        """
        Calculate new price with momentum, trends, and mean reversion.
        
        Args:
            current_price: Current price in Spurs
            volatility: Stock volatility (e.g., 0.02 for 2%)
            activity_score: Team activity score from messages
            symbol: Stock symbol for tracking momentum
        
        Returns:
            New price in Spurs
        """
        # Random walk component (Gaussian)
        random_change = random.gauss(0, volatility)
        
        # Activity component (more activity = upward pressure)
        activity_impact = activity_score * config.ACTIVITY_IMPACT
        
        # Momentum component (trends persist)
        current_momentum = self.momentum.get(symbol, 0.0)
        momentum_impact = current_momentum * config.MOMENTUM_IMPACT_FACTOR
        
        # Update momentum with new change
        new_momentum = random_change + activity_impact
        self.momentum[symbol] = new_momentum * 0.7 + current_momentum * config.MOMENTUM_PERSISTENCE_FACTOR
        
        # Mean reversion (pull towards starting price)
        team_config = config.TEAMS.get(symbol)
        if team_config:
            starting_price = team_config['starting_price']
            distance_from_start = (current_price - starting_price) / starting_price
            mean_reversion = -distance_from_start * config.MEAN_REVERSION_STRENGTH
        else:
            mean_reversion = 0
        
        # Total change percentage
        total_change = random_change + activity_impact + momentum_impact + mean_reversion
        
        # Clamp extreme changes (prevent huge spikes/crashes)
        max_change = volatility * config.MAX_VOLATILITY_MULTIPLIER
        total_change = max(-max_change, min(max_change, total_change))
        
        # Calculate new price
        price_change = int(current_price * total_change)
        new_price = current_price + price_change
        
        return new_price
    
    @market_update_loop.before_loop
    async def before_market_update(self):
        """Wait for bot to be ready before starting market updates."""
        # This will be set up in the main bot file
        pass


# Global market simulator instance
simulator = MarketSimulator()
