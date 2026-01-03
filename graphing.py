"""Graphing module for price history visualization."""
import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict
import market
import team_detection
import utils
import config
from logger import logger

# Set dark theme
plt.style.use('dark_background')


def _ensure_graph_dir():
    """Ensure graph directory exists."""
    os.makedirs(config.GRAPH_DIR, exist_ok=True)


async def generate_price_graph(symbol: str, days: int = 7) -> str:
    """
    Generate a price history graph for a stock.
    
    Args:
        symbol: Stock symbol
        days: Number of days to show (not used for now, shows all history)
    
    Returns:
        Path to the generated graph image
    """
    _ensure_graph_dir()
    
    # Get stock info
    stock_info = await market.market.get_stock_info(symbol)
    if not stock_info:
        raise ValueError(f"Stock {symbol} not found")
    
    # Get price history
    history = stock_info['price_history']
    if not history:
        raise ValueError(f"No price history for {symbol}")
    
    # Prepare data
    timestamps = []
    prices = []
    
    for entry in history:
        try:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            price = entry['price'] / config.SPURS_PER_COG  # Convert to Cogs for display
            timestamps.append(timestamp)
            prices.append(price)
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid price history entry for {symbol}: {e}")
            continue
    
    if not timestamps:
        raise ValueError(f"No valid price history for {symbol}")
    
    # Create figure with professional stock chart styling
    fig = plt.figure(figsize=(config.GRAPH_WIDTH, config.GRAPH_HEIGHT), dpi=config.GRAPH_DPI)
    fig.patch.set_facecolor('#0B0E11')
    
    # Main chart
    ax = fig.add_subplot(111)
    ax.set_facecolor('#131722')
    
    # Determine color (green if up, red if down)
    is_bullish = prices[-1] >= prices[0]
    line_color = '#26A69A' if is_bullish else '#EF5350'
    
    # Plot with thicker line for stock-like appearance
    ax.plot(timestamps, prices, linewidth=2, color=line_color, zorder=5, solid_capstyle='round')
    
    # Add area fill with gradient effect
    ax.fill_between(timestamps, prices, alpha=0.2, color=line_color, zorder=1)
    
    # Add high/low markers for recent peaks
    if len(prices) > 5:
        high_idx = prices.index(max(prices[-20:] if len(prices) > 20 else prices))
        low_idx = prices.index(min(prices[-20:] if len(prices) > 20 else prices))
        ax.plot(timestamps[high_idx], prices[high_idx], 'o', color='#26A69A', markersize=6, zorder=6)
        ax.plot(timestamps[low_idx], prices[low_idx], 'o', color='#EF5350', markersize=6, zorder=6)
    
    # Calculate statistics
    team_name = team_detection.get_team_name(symbol)
    current_price = prices[-1]
    open_price = prices[0]
    high_price = max(prices)
    low_price = min(prices)
    price_change = current_price - open_price
    price_change_pct = (price_change / open_price * 100) if open_price != 0 else 0
    
    # Title with stock info
    change_color = '#26A69A' if price_change >= 0 else '#EF5350'
    change_symbol = '+' if price_change >= 0 else ''
    title_text = f'{symbol}  {team_name}     {current_price:.2f}C  {change_symbol}{price_change:.2f} ({change_symbol}{price_change_pct:.1f}%)'
    ax.text(0.01, 1.05, title_text, transform=ax.transAxes, fontsize=13, 
            fontweight='bold', color='#D1D4DC', verticalalignment='top')
    
    # Add OHLC info
    info_text = f'O: {open_price:.2f}  H: {high_price:.2f}  L: {low_price:.2f}  C: {current_price:.2f}'
    ax.text(0.01, 0.98, info_text, transform=ax.transAxes, fontsize=9,
            color='#787B86', verticalalignment='top')
    
    # Remove axis labels (cleaner)
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # Format x-axis like real stock charts
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    # Style ticks
    ax.tick_params(axis='x', colors='#787B86', labelsize=8, length=0, pad=8)
    ax.tick_params(axis='y', colors='#787B86', labelsize=9, length=0, pad=8)
    
    # Grid - horizontal lines only, very subtle
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='#2A2E39', alpha=0.5, zorder=0)
    ax.xaxis.grid(False)
    
    # Remove all spines except bottom
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#2A2E39')
    ax.spines['bottom'].set_linewidth(1)
    
    # Add price markers on right side
    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()
    
    # Set margins for cleaner look
    ax.margins(x=0.02, y=0.1)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(config.GRAPH_DIR, f'{symbol}_price_history.png')
    plt.savefig(output_path, dpi=config.GRAPH_DPI, bbox_inches='tight')
    plt.close(fig)
    
    return output_path


async def generate_comparison_graph(symbols: List[str]) -> str:
    """
    Generate a comparison graph for multiple stocks.
    
    Args:
        symbols: List of stock symbols to compare
    
    Returns:
        Path to the generated graph image
    """
    _ensure_graph_dir()
    
    if not symbols:
        raise ValueError("No symbols provided")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(config.GRAPH_WIDTH, config.GRAPH_HEIGHT), dpi=config.GRAPH_DPI)
    
    colors = ['#5865F2', '#57F287', '#FEE75C', '#ED4245', '#EB459E', '#F26522']
    
    for idx, symbol in enumerate(symbols):
        stock_info = await market.market.get_stock_info(symbol)
        if not stock_info:
            continue
        
        history = stock_info['price_history']
        if not history:
            continue
        
        timestamps = []
        prices = []
        
        for entry in history:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                price = entry['price'] / config.SPURS_PER_COG
                timestamps.append(timestamp)
                prices.append(price)
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid price history entry: {e}")
                continue
        
        if timestamps:
            team_name = team_detection.get_team_name(symbol)
            color = colors[idx % len(colors)]
            ax.plot(timestamps, prices, linewidth=2.5, label=f'{symbol} - {team_name}', color=color, alpha=0.9)
    
    # Format
    ax.set_title('Stock Price Comparison', fontsize=16, fontweight='bold', color='white')
    ax.set_xlabel('Time', fontsize=12, color='white')
    ax.set_ylabel('Price (Cogs)', fontsize=12, color='white')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    
    # Grid and legend with custom colors
    ax.grid(True, alpha=0.2, linestyle='--', color='#99AAB5')
    legend = ax.legend(loc='best', fontsize=10, framealpha=0.9)
    legend.get_frame().set_facecolor('#2C2F33')
    legend.get_frame().set_edgecolor('#5865F2')
    for text in legend.get_texts():
        text.set_color('white')
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('#2C2F33')
        spine.set_linewidth(1.5)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(config.GRAPH_DIR, 'price_comparison.png')
    plt.savefig(output_path, dpi=config.GRAPH_DPI, bbox_inches='tight')
    plt.close(fig)
    
    return output_path


async def generate_portfolio_graph(user_id: int, history_data: List[Dict]) -> str:
    """
    Generate a portfolio value graph over time.
    
    Args:
        user_id: User ID
        history_data: List of dicts with 'timestamp' and 'total_value' keys
    
    Returns:
        Path to the generated graph image
    """
    _ensure_graph_dir()
    
    if not history_data:
        raise ValueError("No portfolio history data")
    
    timestamps = []
    values = []
    
    for entry in history_data:
        try:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            value = entry['total_value'] / config.SPURS_PER_COG
            timestamps.append(timestamp)
            values.append(value)
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid portfolio history entry: {e}")
            continue
    
    if not timestamps:
        raise ValueError("No valid portfolio history")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(config.GRAPH_WIDTH, config.GRAPH_HEIGHT), dpi=config.GRAPH_DPI)
    
    # Plot data
    ax.plot(timestamps, values, linewidth=2, color='#57F287')
    ax.fill_between(timestamps, values, alpha=0.3, color='#57F287')
    
    # Format
    ax.set_title('Portfolio Value History', fontsize=16, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Total Value (Cogs)', fontsize=12)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(config.GRAPH_DIR, f'portfolio_{user_id}.png')
    plt.savefig(output_path, dpi=config.GRAPH_DPI, bbox_inches='tight')
    plt.close(fig)
    
    return output_path
