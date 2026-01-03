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
    
    # Create figure with dark theme like TradingView
    fig = plt.figure(figsize=(config.GRAPH_WIDTH, config.GRAPH_HEIGHT), dpi=config.GRAPH_DPI, facecolor='#0D1117')
    ax = fig.add_subplot(111, facecolor='#161B22')
    
    # Plot line with glow effect (TradingView style)
    # Main line
    line_color = '#26A69A' if prices[-1] > prices[0] else '#EF5350'  # Green if up, red if down
    ax.plot(timestamps, prices, linewidth=2.5, color=line_color, label='Price', zorder=3)
    
    # Add subtle glow
    ax.plot(timestamps, prices, linewidth=6, color=line_color, alpha=0.15, zorder=2)
    
    # Fill with gradient (lighter at top)
    ax.fill_between(timestamps, prices, alpha=0.15, color=line_color, zorder=1)
    
    # Calculate and plot moving average (optional, if enough data)
    if len(prices) > 10:
        ma_period = min(10, len(prices) // 3)
        ma_prices = []
        for i in range(len(prices)):
            if i < ma_period:
                ma_prices.append(sum(prices[:i+1]) / (i+1))
            else:
                ma_prices.append(sum(prices[i-ma_period+1:i+1]) / ma_period)
        ax.plot(timestamps, ma_prices, linewidth=1.5, color='#7B68EE', alpha=0.7, linestyle='--', label=f'{ma_period}MA', zorder=2)
    
    # Format with TradingView style
    team_name = team_detection.get_team_name(symbol)
    current_price = prices[-1]
    price_change = prices[-1] - prices[0]
    price_change_pct = (price_change / prices[0] * 100) if prices[0] != 0 else 0
    change_emoji = '▲' if price_change > 0 else '▼'
    
    ax.set_title(
        f'{symbol} - {team_name}  |  {current_price:.2f}C {change_emoji}{abs(price_change_pct):.1f}%',
        fontsize=14, fontweight='bold', color='#C9D1D9', pad=20
    )
    ax.set_xlabel('', fontsize=10)  # No label, cleaner look
    ax.set_ylabel('Price (Cogs)', fontsize=11, color='#8B949E')
    
    # Format x-axis (TradingView style - cleaner)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), color='#8B949E', fontsize=9)
    plt.setp(ax.yaxis.get_majorticklabels(), color='#8B949E', fontsize=9)
    
    # Grid with TradingView style (horizontal only, subtle)
    ax.grid(True, axis='y', alpha=0.1, linestyle='-', color='#30363D', linewidth=0.8)
    ax.grid(False, axis='x')
    
    # Remove top and right spines (TradingView style)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#30363D')
    ax.spines['bottom'].set_color('#30363D')
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # Add legend with dark theme
    legend = ax.legend(loc='upper left', framealpha=0.9, facecolor='#161B22', edgecolor='#30363D')
    plt.setp(legend.get_texts(), color='#8B949E', fontsize=9)
    
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
