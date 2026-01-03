# Feature Documentation

Complete guide to all the advanced trading features in GSC.

## Table of Contents
- [Limit Orders](#limit-orders)
- [Price Alerts](#price-alerts)
- [Portfolio Analytics](#portfolio-analytics)
- [Trade History](#trade-history)
- [Candlestick Charts](#candlestick-charts)
- [Watchlist](#watchlist)
- [Achievements](#achievements)

---

## Limit Orders

### What Are They?
Set orders that automatically buy or sell when a stock hits your target price. No need to watch the market 24/7.

### Commands
- `/limitbuy <symbol> <shares> <price>` - Place a limit buy order
- `/limitsell <symbol> <shares> <price>` - Place a limit sell order
- `/orders` - View all your active limit orders
- `/cancelorder <id>` - Cancel a specific limit order

### How It Works
- **Limit Buy**: Executes when price drops to your target or lower
- **Limit Sell**: Executes when price rises to your target or higher
- Checked every 3 minutes with market updates
- Expires after 24 hours if not triggered

### Example
```
/limitbuy STMP 50 12.5
```
This will automatically buy 50 shares of STMP when the price drops to 12.5 Cogs or lower.

### Limits
- Need enough cash for buy orders
- Need enough shares for sell orders
- Max 10 active orders at once
- Validated when you place them

---

## Price Alerts

### What Are They?
Get DM'd when a stock hits your target price. Simple as that.

### Commands
- `/alert <symbol> <condition> <price>` - Set a price alert
  - Condition: `above` or `below`
- `/alerts` - View all your active alerts
- `/removealert <id>` - Remove a specific alert

### How It Works
- Checked every minute
- You get a DM when triggered
- Auto-deleted after firing
- Max 10 alerts at once

### Example
```
/alert ROSE above 25
```
You'll receive a DM when ROSE rises above 25 Cogs.

---

## Portfolio Analytics

### What Is It?
See your portfolio as a pie chart with profit/loss tracking.

### Command
- `/portfolio` - View detailed portfolio analysis

### Features
- **Pie Chart**: Visual breakdown of holdings and cash
- **Total Value**: Combined stock value + cash balance
- **P/L Tracking**: Per-stock and total profit/loss
- **ROI**: Return on investment percentages
- **Top Holdings**: Shows your 3 largest positions

### What You See
- Total value (stocks + cash)
- How much you invested vs what it's worth now
- Profit/loss in Cogs and %
- Performance per stock
- Pie chart of your holdings

---

## Trade History

### What Is It?
Look back at your past trades and see if you made or lost money.

### Command
- `/history [days] [symbol]` - View trade history
  - `days`: 1-30 (default: 7)
  - `symbol`: Filter by specific stock (optional)

### Features
- **Summary Statistics**: Total buys/sells per stock
- **Recent Trades**: Last 10 transactions with details
- **Net P/L**: Profit/loss for the period
- **Trade Volume**: Shares and Cog values
- **Timestamps**: Relative time display (e.g., "2 hours ago")

### What's Tracked
- All your buys and sells
- How many shares
- Price you paid/received
- Total value of each trade
- When it happened

---

## Candlestick Charts

### What Are They?
Those fancy stock market charts with the green and red bars. Shows opening, high, low, and closing prices.

### Command
- `/candlestick <symbol> [hours]` - Generate candlestick chart
  - `hours`: 1-168 (default: 24)

### Features
- **Hourly Candles**: Aggregated hourly OHLC data
- **TradingView Style**: Professional dark theme
- **Color Coding**:
  - Green candles: Bullish (close > open)
  - Red candles: Bearish (close < open)
- **Wicks**: Show high/low price range
- **Time Labels**: Timestamps for each candle

### Details
- Hourly candles made from price snapshots
- Need at least 2 candles to show a chart
- Can show up to 1 week of data

---

## Watchlist

### What Is It?
Keep tabs on stocks you're thinking about buying without actually buying them yet.

### Commands
- `/watch <symbol>` - Add stock to watchlist
- `/unwatch <symbol>` - Remove from watchlist
- `/watchlist` - View watchlist with 24h changes

### Features
- **Price Tracking**: Current prices for watched stocks
- **24h Change**: Percentage change over last 24 hours
- **Quick Access**: See watchlist indicators in `/market`
- **Limit**: Maximum 10 stocks per watchlist

### Use Cases
- Monitor potential investments
- Track competitor stocks
- Watch for entry opportunities
- Research before buying

---

## Achievements

### What Are They?
Badges you unlock by hitting milestones. Gotta catch 'em all.

### Command
- `/achievements` - View unlocked achievements and progress

### Achievement List

#### Common
- 🎯 **First Trade** - Made your first trade

#### Uncommon
- 💎 **Diamond Hands** - Held a stock for 7+ days
- 📊 **Day Trader** - Made 10+ trades in one day

#### Rare
- 💰 **Millionaire** - Reached 1M Spurs total value
- ⏰ **Perfect Timing** - Sold a stock for 50%+ profit
- 🌈 **Diversified** - Own stocks in all 6 teams

#### Epic
- 🐋 **Whale** - Made a single trade worth 100k+ Cogs
- 🎰 **High Roller** - Own 1000+ shares of a single stock

#### Legendary
- 🐦 **Early Bird** - Bought a stock at its all-time low
- 👑 **Market Master** - Unlocked all other achievements

### How They Work
- Auto-checked when you trade or check your portfolio
- Progress bar shows how close you are to completing them all
- Locked ones show you what you need to do

---

## Database Schema

Here's the database structure for the new features:

```sql
-- Limit orders
CREATE TABLE limit_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    order_type TEXT NOT NULL,  -- 'buy' or 'sell'
    shares INTEGER NOT NULL,
    target_price INTEGER NOT NULL,  -- in Spurs
    created_at TEXT NOT NULL,
    expires_at TEXT
);

-- Price alerts
CREATE TABLE price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    condition TEXT NOT NULL,  -- 'above' or 'below'
    target_price INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

-- Watchlist
CREATE TABLE watchlist (
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    added_at TEXT NOT NULL,
    PRIMARY KEY (user_id, symbol)
);

-- Achievements
CREATE TABLE achievements (
    user_id INTEGER NOT NULL,
    achievement_id TEXT NOT NULL,
    unlocked_at TEXT NOT NULL,
    PRIMARY KEY (user_id, achievement_id)
);

-- Portfolio snapshots (for historical tracking)
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_value INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);
```

---

## Configuration

Everything works out of the box. No setup needed.

### Limits
Defined in respective modules:
- Limit orders: 10 per user
- Price alerts: 10 per user
- Watchlist: 10 stocks per user
- Order expiration: 24 hours
- Alert check interval: 60 seconds

### Performance Notes
- Limit orders run with market updates (every 3 min)
- Alerts checked every minute
- Achievements track on trades/portfolio checks
- Database queries are optimized

---

## Need Help?

- Use `/help` in Discord
- Check the bot console logs
- Open an issue on GitHub if something's broken
