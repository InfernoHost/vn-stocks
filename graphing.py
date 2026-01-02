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
        except (ValueError, KeyError):
            continue
    
    if not timestamps:
        raise ValueError(f"No valid price history for {symbol}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(config.GRAPH_WIDTH, config.GRAPH_HEIGHT), dpi=config.GRAPH_DPI)
    
    # Plot data with gradient color
    ax.plot(timestamps, prices, linewidth=2.5, color='#5865F2', label='Price')
    ax.fill_between(timestamps, prices, alpha=0.4, color='#5865F2')
    
    # Format
    team_name = team_detection.get_team_name(symbol)
    ax.set_title(f'{symbol} - {team_name} Price History', fontsize=16, fontweight='bold', color='white')
    ax.set_xlabel('Time', fontsize=12, color='white')
    ax.set_ylabel('Price (Cogs)', fontsize=12, color='white')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    
    # Grid with custom color
    ax.grid(True, alpha=0.2, linestyle='--', color='#99AAB5')
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('#2C2F33')
        spine.set_linewidth(1.5)
    
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
            except (ValueError, KeyError):
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
        except (ValueError, KeyError):
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
