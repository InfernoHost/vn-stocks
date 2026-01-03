"""Market data storage using JSON files."""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import aiofiles
import config
from logger import logger
import validators


class MarketData:
    """Manages stock prices and activity tracking."""
    
    def __init__(self):
        self.data_dir = config.MARKET_DATA_DIR
        self.activity_scores = {symbol: 0 for symbol in config.TEAMS.keys()}
        self._lock = asyncio.Lock()
        # In-memory cache for frequently accessed stock data
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 5.0  # Cache TTL in seconds
    
    def _get_stock_file(self, symbol: str) -> str:
        """Get the file path for a stock's JSON file."""
        # Validate and sanitize symbol to prevent path traversal
        if not validators.validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        sanitized_symbol = validators.sanitize_symbol(symbol)
        filepath = os.path.join(self.data_dir, f"{sanitized_symbol}.json")
        
        # Verify path is within data directory
        if not validators.validate_filepath(filepath, self.data_dir):
            raise ValueError(f"Invalid file path for symbol: {symbol}")
        
        return filepath
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self._cache:
            return False
        
        import time
        timestamp = self._cache_timestamps.get(symbol, 0)
        return (time.time() - timestamp) < self._cache_ttl
    
    def _invalidate_cache(self, symbol: str):
        """Invalidate cache for a specific symbol."""
        self._cache.pop(symbol, None)
        self._cache_timestamps.pop(symbol, None)
    
    async def initialize(self):
        """Set up data directory and create stock files."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        for symbol, team in config.TEAMS.items():
            stock_file = self._get_stock_file(symbol)
            
            if not os.path.exists(stock_file):
                # Create new stock file
                stock_data = {
                    'team_name': team['name'],
                    'symbol': symbol,
                    'starting_price': team['starting_price'],
                    'current_price': team['starting_price'],
                    'volatility': team['volatility'],
                    'price_history': [
                        {
                            'timestamp': datetime.utcnow().isoformat(),
                            'price': team['starting_price']
                        }
                    ]
                }
                await self._write_stock_data(symbol, stock_data)
    
    async def _read_stock_data(self, symbol: str) -> Optional[Dict]:
        """Read stock data from JSON file with caching."""
        # Check cache first
        if self._is_cache_valid(symbol):
            return self._cache[symbol].copy()
        
        try:
            stock_file = self._get_stock_file(symbol)
        except ValueError as e:
            logger.error(f"Invalid symbol in _read_stock_data: {e}")
            return None
        
        if not os.path.exists(stock_file):
            return None
        
        try:
            # Async file reading without holding lock during I/O
            async with aiofiles.open(stock_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            # Update cache
            import time
            self._cache[symbol] = data
            self._cache_timestamps[symbol] = time.time()
            
            return data.copy()
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON for {symbol}: {e}")
            return None
        except IOError as e:
            logger.error(f"Failed to read {stock_file}: {e}")
            return None
    
    async def _write_stock_data(self, symbol: str, data: Dict):
        """Write stock data to JSON file asynchronously."""
        try:
            stock_file = self._get_stock_file(symbol)
        except ValueError as e:
            logger.error(f"Invalid symbol in _write_stock_data: {e}")
            return
        
        try:
            # Serialize JSON first (CPU-bound operation outside lock)
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Lock only for write operation
            async with self._lock:
                async with aiofiles.open(stock_file, 'w', encoding='utf-8') as f:
                    await f.write(json_content)
            
            # Invalidate cache after successful write
            self._invalidate_cache(symbol)
        except IOError as e:
            logger.error(f"Failed to write {stock_file}: {e}")
    
    async def get_price(self, symbol: str) -> Optional[int]:
        """Get current price for a stock."""
        data = await self._read_stock_data(symbol)
        if data:
            return data['current_price']
        return None
    
    async def get_all_prices(self) -> Dict[str, int]:
        """Get current prices for all stocks."""
        prices = {}
        for symbol in config.TEAMS.keys():
            price = await self.get_price(symbol)
            if price is not None:
                prices[symbol] = price
        return prices
    
    async def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get full stock information."""
        return await self._read_stock_data(symbol)
    
    async def get_all_stocks(self) -> List[Dict]:
        """Get information for all stocks."""
        stocks = []
        for symbol in config.TEAMS.keys():
            stock_data = await self._read_stock_data(symbol)
            if stock_data:
                stocks.append(stock_data)
        return stocks
    
    async def update_price(self, symbol: str, new_price: int):
        """Update stock price and append to history."""
        data = await self._read_stock_data(symbol)
        if not data:
            return
        
        data['current_price'] = new_price
        
        # Append to history
        data['price_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'price': new_price
        })
        
        # Trim history if too long
        if len(data['price_history']) > config.PRICE_HISTORY_MAX:
            data['price_history'] = data['price_history'][-config.PRICE_HISTORY_MAX:]
        
        await self._write_stock_data(symbol, data)
    
    async def update_prices_batch(self, updates: Dict[str, int]):
        """Update multiple stock prices in batch for better performance."""
        tasks = []
        for symbol, new_price in updates.items():
            tasks.append(self.update_price(symbol, new_price))
        await asyncio.gather(*tasks)
    
    async def reset_prices(self):
        """Reset all stock prices to starting values."""
        for symbol, team in config.TEAMS.items():
            data = await self._read_stock_data(symbol)
            if data:
                data['current_price'] = team['starting_price']
                data['price_history'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'price': team['starting_price']
                })
                await self._write_stock_data(symbol, data)
    
    async def get_price_history(self, symbol: str, limit: Optional[int] = None) -> List[Dict]:
        """Get price history for a stock."""
        data = await self._read_stock_data(symbol)
        if not data:
            return []
        
        history = data['price_history']
        if limit:
            return history[-limit:]
        return history
    
    def increment_activity(self, symbol: str):
        """Increment activity score for a team."""
        if symbol in self.activity_scores:
            self.activity_scores[symbol] += 1
    
    def get_activity_score(self, symbol: str) -> int:
        """Get activity score for a team."""
        return self.activity_scores.get(symbol, 0)
    
    def decay_activity(self):
        """Decay all activity scores."""
        for symbol in self.activity_scores:
            self.activity_scores[symbol] *= config.ACTIVITY_DECAY
    
    def reset_activity(self):
        """Reset all activity scores to zero."""
        self.activity_scores = {symbol: 0 for symbol in config.TEAMS.keys()}


# Global market data instance
market = MarketData()
