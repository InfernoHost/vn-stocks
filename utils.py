"""Currency conversion and formatting utilities."""
import config


def spurs_to_cogs_display(spurs: int) -> str:
    """Convert Spurs to readable format (e.g., '5 Cogs 32 Spurs')."""
    cogs = spurs // config.SPURS_PER_COG
    remaining_spurs = spurs % config.SPURS_PER_COG
    
    cog_word = "Cog" if cogs == 1 else "Cogs"
    spur_word = "Spur" if remaining_spurs == 1 else "Spurs"
    
    return f"{cogs} {cog_word} {remaining_spurs} {spur_word}"


def cogs_to_spurs(cogs: int) -> int:
    """Convert Cogs to Spurs (1 Cog = 64 Spurs)."""
    return cogs * config.SPURS_PER_COG


def parse_price_input(price_str: str) -> int:
    """Parse user price input and convert to Spurs."""
    try:
        cogs = int(price_str)
        return cogs_to_spurs(cogs)
    except ValueError:
        raise ValueError("Invalid price format")


def format_price(spurs: int) -> str:
    """Format price for display."""
    return spurs_to_cogs_display(spurs)


def calculate_total_value(balance: int, portfolio: list, prices: dict) -> int:
    """
    Calculate total value (balance + portfolio value).
    
    Args:
        balance: Player balance in Spurs
        portfolio: List of holdings (dicts with 'symbol' and 'shares')
        prices: Dict of current prices {symbol: price_in_spurs}
    
    Returns:
        Total value in Spurs
    """
    total = balance
    
    for holding in portfolio:
        symbol = holding['symbol']
        shares = holding['shares']
        price = prices.get(symbol, 0)
        total += shares * price
    
    return total


def calculate_profit_loss(avg_cost: int, current_price: int, shares: int) -> tuple[int, float]:
    """
    Calculate profit/loss for a holding.
    
    Args:
        avg_cost: Average cost per share in Spurs
        current_price: Current price per share in Spurs
        shares: Number of shares
    
    Returns:
        Tuple of (total_pl_in_spurs, percentage)
    """
    cost_basis = avg_cost * shares
    current_value = current_price * shares
    pl = current_value - cost_basis
    
    if cost_basis > 0:
        percentage = (pl / cost_basis) * 100
    else:
        percentage = 0.0
    
    return pl, percentage
