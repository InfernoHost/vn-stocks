# Commands Reference 📋

Complete list of all available commands in GSC.

## Basic Commands 🎯

### Account Management

**/register**

Create your trading account and receive 10 Cogs starting capital

---

**/balance**

Check your current cash balance and portfolio value

### Trading

**/buy symbol:[SYMBOL] shares:[NUMBER]**

Buy shares at current market price

Example: `/buy symbol:STMP shares:10`

---

**/sell symbol:[SYMBOL] shares:[NUMBER]**

Sell shares at current market price

Example: `/sell symbol:VIOL shares:5`

## Market Information 📊

**/market**

View all available stocks with current prices and 24h changes

---

**/stock symbol:[SYMBOL]**

Get detailed information about a specific stock

Example: `/stock symbol:CRAV`

---

**/leaderboard**

See top 10 richest traders by total net worth

## Charts & Analysis 📈

**/graph symbol:[SYMBOL]**

Display live-updating line chart with TradingView styling. Updates every 30 seconds, auto-stops after 120s inactivity

Example: `/graph symbol:STMP`

---

**/candlestick symbol:[SYMBOL] period:[24h|7d|30d]**

Show OHLC candlestick chart

Example: `/candlestick symbol:ROSE period:24h`

---

**/portfolio**

View your holdings with P/L tracking and pie chart visualization

## Limit Orders ⚡

**/limitbuy symbol:[SYMBOL] shares:[NUMBER] price:[PRICE]**

Create automatic buy order at target price

Example: `/limitbuy symbol:POT shares:20 price:11`

---

**/limitsell symbol:[SYMBOL] shares:[NUMBER] price:[PRICE]**

Create automatic sell order at target price

Example: `/limitsell symbol:VIOL shares:15 price:25`

---

**/orders**

List all your active limit orders with details

---

**/cancelorder order_id:[ID]**

Cancel a specific limit order

Example: `/cancelorder order_id:1`

## Price Alerts 🔔

**/alert symbol:[SYMBOL] type:[above|below] price:[PRICE]**

Set price alert for DM notification

Example: `/alert symbol:CRAV type:above price:30`

---

**/alerts**

View all your active price alerts

---

**/removealert alert_id:[ID]**

Remove a specific price alert

Example: `/removealert alert_id:1`

## Tracking & History 📜

**/history [symbol:SYMBOL]**

View your trade history with P/L calculations. Optional: Filter by symbol

Example: `/history symbol:STMP`

---

**/watch symbol:[SYMBOL]**

Add stock to watchlist (max 10)

Example: `/watch symbol:POT`

---

**/unwatch symbol:[SYMBOL]**

Remove stock from watchlist

Example: `/unwatch symbol:POT`

---

**/watchlist**

View all watched stocks with 24h price changes

## Achievements 🏆

**/achievements**

View all available achievements and your progress

## Information & Help ℹ️

**/help**

Display comprehensive help message with command categories

---

**/activity**

Show current market activity by team (message counts)

## Admin Commands 👑

**(Requires Admin role)**

**/give user:[USER] amount:[AMOUNT]**

Give money to a player

Example: `/give user:@Player amount:50`

---

**/setprice symbol:[SYMBOL] price:[PRICE]**

Manually set stock price

Example: `/setprice symbol:STMP price:20`

---

**/resetmarket**

Reset all stock prices to starting values (DANGEROUS)

## Quick Reference Table

| Category | Commands | Purpose |
|----------|----------|---------|
| **Setup** | `/register`, `/balance` | Account creation |
| **Trading** | `/buy`, `/sell` | Basic transactions |
| **Market** | `/market`, `/stock`, `/leaderboard` | Price info |
| **Charts** | `/graph`, `/candlestick`, `/portfolio` | Visualization |
| **Automation** | `/limitbuy`, `/limitsell`, `/orders` | Limit orders |
| **Alerts** | `/alert`, `/alerts`, `/removealert` | Price notifications |
| **Tracking** | `/history`, `/watch`, `/watchlist` | Monitoring |
| **Progress** | `/achievements` | Badges |
| **Help** | `/help`, `/activity` | Information |
| **Admin** | `/give`, `/setprice`, `/resetmarket` | Management |

## Stock Symbols

All commands use these symbols:
- `STMP` - Steamporium
- `ROSE` - Rosebud
- `VIOL` - Violetvale
- `POT` - Potpourri
- `CRAV` - Cravat
- `VOC` - Voco

## Price Format

- Prices always in **Cogs** (e.g., `15.75`)
- Bot handles Spur conversion automatically
- Supports decimals for precise pricing

## Common Workflows

**Check then buy:**
```
/market → /stock symbol:STMP → /buy symbol:STMP shares:10
```

**Monitor then alert:**
```
/watch symbol:VIOL → /alert symbol:VIOL type:above price:25
```

**Analyze then trade:**
```
/graph symbol:CRAV → /candlestick symbol:CRAV period:24h → /buy
```

## Next Steps

- [Home](/) - Overview and introduction
- [Getting Started](/getting-started) - Basics tutorial
- [Trading Strategies](/trading) - Learn to trade effectively
- [Advanced Features](/advanced) - Limit orders, alerts, etc.
- [FAQ](/faq) - Common questions

::: tip Bookmark This Page
Use it as your quick reference guide while trading in Discord!
:::
