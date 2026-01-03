"""Candlestick chart generation for OHLC data."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
import market
import team_detection
import utils
import config
from logger import logger


async def generate_candlestick_chart(symbol: str, hours: int = 24) -> str:
    """
    Generate a candlestick chart for OHLC data.
    
    Args:
        symbol: Stock symbol
        hours: Number of hours to show
    
    Returns:
        Path to generated chart
    """
    os.makedirs(config.GRAPH_DIR, exist_ok=True)
    
    # Get OHLC data (aggregated from price history)
    stock_info = await market.market.get_stock_info(symbol)
    if not stock_info:
        raise ValueError(f"Stock {symbol} not found")
    
    history = stock_info['price_history']
    if not history:
        raise ValueError(f"No price history for {symbol}")
    
    # Aggregate into hourly OHLC candles
    candles = _aggregate_to_ohlc(history, interval_minutes=60)
    
    if not candles:
        raise ValueError(f"Insufficient data for candlestick chart")
    
    # Limit to specified hours
    cutoff = datetime.now() - timedelta(hours=hours)
    candles = [c for c in candles if c['time'] >= cutoff]
    
    if len(candles) < 2:
        raise ValueError(f"Insufficient recent data (need at least 2 candles)")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    fig.patch.set_facecolor('#0B0E11')
    ax.set_facecolor('#131722')
    
    # Draw candlesticks
    for i, candle in enumerate(candles):
        time = candle['time']
        open_price = candle['open'] / config.SPURS_PER_COG
        high = candle['high'] / config.SPURS_PER_COG
        low = candle['low'] / config.SPURS_PER_COG
        close = candle['close'] / config.SPURS_PER_COG
        
        # Determine color
        is_bullish = close >= open_price
        body_color = '#26A69A' if is_bullish else '#EF5350'
        wick_color = body_color
        
        # Draw wick (high-low line)
        ax.plot([i, i], [low, high], color=wick_color, linewidth=1, zorder=1)
        
        # Draw body (open-close rectangle)
        body_height = abs(close - open_price)
        body_bottom = min(open_price, close)
        
        if body_height > 0:
            rect = Rectangle(
                (i - 0.3, body_bottom),
                0.6,
                body_height,
                facecolor=body_color,
                edgecolor=body_color,
                linewidth=0,
                zorder=2
            )
            ax.add_patch(rect)
        else:
            # Doji (open == close)
            ax.plot([i - 0.3, i + 0.3], [open_price, open_price],
                   color=body_color, linewidth=2, zorder=2)
    
    # Styling
    team_name = team_detection.get_team_name(symbol)
    current_price = candles[-1]['close'] / config.SPURS_PER_COG
    
    ax.set_title(
        f"{symbol} - {team_name}",
        color='#C9D1D9',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    
    # X-axis: Show times
    time_labels = [c['time'].strftime('%H:%M') for c in candles]
    ax.set_xticks(range(len(candles)))
    ax.set_xticklabels(time_labels, rotation=45, ha='right', color='#787B86', fontsize=9)
    
    # Y-axis: Price
    ax.set_ylabel('Price (Cogs)', color='#787B86', fontsize=10)
    ax.tick_params(axis='y', labelcolor='#787B86', labelsize=9)
    
    # Grid
    ax.grid(True, alpha=0.1, color='#787B86', linestyle='--', linewidth=0.5)
    
    # Price on right side
    ax2 = ax.twinx()
    ax2.set_ylabel(f'{current_price:.2f} Cogs', color='#C9D1D9', fontsize=10, fontweight='bold')
    ax2.set_ylim(ax.get_ylim())
    ax2.tick_params(axis='y', labelcolor='#787B86', labelsize=9)
    
    # Remove borders
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(config.GRAPH_DIR, f'{symbol}_candlestick.png')
    plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='#0B0E11')
    plt.close(fig)
    
    logger.info(f"Generated candlestick chart: {output_path}")
    return output_path


def _aggregate_to_ohlc(history, interval_minutes=60):
    """Aggregate price history into OHLC candles."""
    if not history:
        return []
    
    candles = []
    current_candle = None
    
    for entry in history:
        try:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            price = entry['price']
            
            # Round timestamp to interval
            interval_start = timestamp.replace(
                minute=(timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0
            )
            
            if current_candle is None or current_candle['time'] != interval_start:
                # Start new candle
                if current_candle is not None:
                    candles.append(current_candle)
                
                current_candle = {
                    'time': interval_start,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price
                }
            else:
                # Update current candle
                current_candle['high'] = max(current_candle['high'], price)
                current_candle['low'] = min(current_candle['low'], price)
                current_candle['close'] = price
        
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid entry in history: {e}")
            continue
    
    # Add last candle
    if current_candle is not None:
        candles.append(current_candle)
    
    return candles
