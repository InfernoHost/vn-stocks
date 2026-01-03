# Advanced Features ⚡

Take your trading to the next level with powerful automation and analysis tools.

## Limit Orders 🎯

### What Are Limit Orders?

Limit orders let you set automatic buy/sell orders that execute when prices hit your target - even while you're offline!

**Benefits:**
- Trade 24/7 without watching charts
- Never miss perfect entry/exit points
- Remove emotion from trading decisions
- Secure profits automatically

### Creating Limit Buy Orders

Buy stocks automatically when price drops to your target.

**/limitbuy symbol:STMP shares:10 price:18**

Buys 10 STMP shares if price drops to 18 Cogs or lower

**Real-world scenario:**
```
Current situation:
- STMP trading at 22 Cogs (too expensive for you)
- You want to buy at 18 Cogs (good value)
- You're going to bed soon

Action:
/limitbuy symbol:STMP shares:10 price:18

What happens:
- Order sits waiting (shows in /orders)
- Overnight, STMP drops to 17.8 Cogs
- Order executes automatically!
- You wake up owning 10 STMP at 17.8 Cogs
- Cost: 178 Cogs deducted from balance
```

::: tip Pro Tip
Set limit buys 10-15% below current price to catch dips
:::

### Creating Limit Sell Orders

Sell stocks automatically when price rises to your target.

**/limitsell symbol:VIOL shares:15 price:25**

Sells 15 VIOL shares if price rises to 25 Cogs or higher

**Real-world scenario:**
```
Current situation:
- You own 15 VIOL bought at 18 Cogs
- VIOL currently at 20 Cogs
- You want to sell at 25 Cogs (39% profit)
- You'll be at work all day

Action:
/limitsell symbol:VIOL shares:15 price:25

What happens:
- Order waits in queue
- During the day, VIOL spikes to 25.4 Cogs
- Order executes at 25 Cogs!
- You get 375 Cogs (15 × 25)
- Profit: 105 Cogs (+39%) secured
```

::: tip Strategy
Use limit sells to lock in 20-30% profits automatically
:::

### Managing Your Orders

View all active limit orders:

**/orders**

Lists all pending limit orders with details

**Example output:**
```
📋 Your Active Limit Orders
━━━━━━━━━━━━━━━━━━━━━━━━━━

Order #1 (Buy)
Symbol: STMP
Shares: 10
Target Price: 18 Cogs
Current Price: 22 Cogs
Status: Waiting (needs -18% drop)
Expires: Jan 5, 2026 10:30 AM
```

Cancel an order:

**/cancelorder order_id:1**

Cancels order #1 (get ID from /orders)

### Limit Order Rules

::: warning Important Rules
**Expiration:** All orders expire after **24 hours**

**Balance requirements:**
- Buy orders: Money reserved when order created
- Sell orders: Shares must be in portfolio

**Execution:** Orders execute during market updates (every 3 minutes)

**Limits:** Maximum **10 active orders** per user
:::

## Price Alerts 🔔

### What Are Price Alerts?

Get instant Discord DM when a stock hits your target price - no need to watch charts!

**Benefits:**
- Never miss important price levels
- Monitor multiple stocks simultaneously
- Perfect for busy traders
- Catch opportunities while offline

### Setting Alerts Above Current Price

Get notified when price goes up:

**/alert symbol:CRAV type:above price:30**

DMs you when CRAV price rises above 30 Cogs

**Use case - Sell signal:**
```
Situation:
- You own 20 CRAV bought at 25 Cogs
- Want to sell at 30 Cogs (+20% profit)
- Don't want to check price every hour

Action:
/alert symbol:CRAV type:above price:30

Result:
- CRAV price hits 30.2 Cogs
- Bot DMs you: "🔔 CRAV is now 30.2 Cogs (above your 30 Cogs alert)"
- You quickly /sell symbol:CRAV shares:20
- Profit secured!
```

### Setting Alerts Below Current Price

Get notified when price goes down:

**/alert symbol:ROSE type:below price:12**

DMs you when ROSE price drops below 12 Cogs

**Use case - Buy signal:**
```
Situation:
- ROSE currently at 15 Cogs
- You think 12 Cogs is great value
- Waiting for a dip to buy

Action:
/alert symbol:ROSE type:below price:12

Result:
- Market correction, ROSE drops to 11.8 Cogs
- Bot DMs you: "🔔 ROSE is now 11.8 Cogs (below your 12 Cogs alert)"
- You buy 30 shares at discount
- Later sell at 14 Cogs for +18% profit
```

### Managing Alerts

View all active alerts:

**/alerts**

Lists all your price alerts

Remove an alert:

**/removealert alert_id:1**

Removes alert #1 (get ID from /alerts)

### Alert Behavior 🎯

::: info Alert Details
**One-time use:** Alerts trigger once, then auto-delete

**Checking frequency:** Every 60 seconds

**Instant notifications:** DM sent immediately when price hits

**No limits:** Set as many alerts as you want!
:::

## Watchlist 👀

### What Is a Watchlist?

Track stocks you're interested in without owning them - see price changes at a glance.

**Benefits:**
- Monitor potential buys
- Track competitors
- See sector trends
- Quick price overview

### Adding Stocks to Watchlist

**/watch symbol:POT**

Adds POT to your watchlist

### Viewing Your Watchlist

**/watchlist**

Shows all watched stocks with 24h changes

**Example output:**
```
👀 Your Watchlist
━━━━━━━━━━━━━━━━━━━━

POT: 12.45 Cogs (+3.2%)
STMP: 20.87 Cogs (-1.5%)
CRAV: 28.12 Cogs (+5.7%)
VIOL: 19.03 Cogs (+2.1%)

💰 Cash Available: 125 Cogs
```

### Removing from Watchlist

**/unwatch symbol:POT**

Removes POT from watchlist

**Limits:** Maximum **10 stocks** on watchlist

## Trade History 📜

### Viewing Your Trades

See all past transactions with P/L calculations:

**/history**

Shows recent transaction history

**Example output:**
```
📜 Trading History
━━━━━━━━━━━━━━━━━━━━

Jan 3, 10:45 AM
SOLD 10 STMP @ 22.5 Cogs
Total: 225 Cogs
P/L: +25 Cogs (+12.5%)

Jan 3, 9:30 AM
BOUGHT 10 STMP @ 20 Cogs
Total: 200 Cogs
```

### Filtering History

View trades for specific stock:

**/history symbol:STMP**

Shows only STMP trades

## Portfolio Analytics 📊

### Advanced Portfolio View

**/portfolio**

Shows detailed holdings with pie chart

**What you get:**
- Holdings breakdown: Each stock's current value
- Profit/Loss: Per position and total
- ROI percentage: Return on investment
- Asset allocation: Visual pie chart
- Total net worth: Cash + holdings

## Candlestick Charts 📉

### What Are Candlestick Charts?

Professional-grade OHLC (Open-High-Low-Close) charts showing price patterns.

**/candlestick symbol:STMP period:24h**

Shows hourly candlesticks for last 24 hours

**What you see:**
- **Green candles:** Price went up that hour
- **Red candles:** Price went down
- **Wicks:** Show high/low extremes
- **Body:** Shows open/close prices

**Available periods:**
- `24h` - Last 24 hours (hourly candles)
- `7d` - Last 7 days (daily candles)
- `30d` - Last 30 days (daily candles)

### Reading Candles

**Bullish patterns (buy signals):**
- Multiple green candles in a row
- Long green candles (strong buying)
- Small red candles after big drop (reversal)

**Bearish patterns (sell signals):**
- Multiple red candles in a row
- Long red candles (strong selling)
- Small green candles after big rise (exhaustion)

::: tip Pro Tip
Use candlesticks with `/graph` for complete technical analysis
:::

## Achievements System 🏆

### Earning Badges

Unlock rare achievements by trading and reaching milestones!

**/achievements**

Shows all achievements and your progress

### Achievement List

**Common (Easy to get):**
- 🎯 **First Trade** - Complete your first transaction
- 💰 **Profit Taker** - Make 50+ Cogs profit on a trade

**Uncommon (Medium difficulty):**
- 💎 **Diamond Hands** - Hold a stock for 7+ days
- 📈 **Bull Market** - Earn 100+ Cogs total profit
- 🏆 **Millionaire** - Reach 100 Cogs net worth

**Rare (Challenging):**
- 🐋 **Whale** - Own 1000+ total shares
- 🎰 **High Roller** - Complete 100+ trades
- 📊 **Diversified** - Own shares in 5+ different stocks

**Epic (Very hard):**
- 🔥 **Hot Streak** - Win 10 profitable trades in a row
- 👑 **Market Leader** - Reach #1 on leaderboard

**Legendary (Extremely rare):**
- 🌟 **Moon Mission** - 1000%+ profit on a single trade

::: tip Bragging Rights
Show off your achievements in Discord!
:::

## Tips for Power Users

### Combine Tools for Maximum Effect

**Example workflow:**
```
1. Add stocks to watchlist (/watch)
2. Set price alerts for buy points (/alert type:below)
3. When alerted, check /candlestick for confirmation
4. Place limit buy orders (/limitbuy)
5. Set sell limit orders for profit targets (/limitsell)
6. Monitor with /portfolio pie charts
7. Track performance in /history
```

### Automation Setup

**While you sleep:**
```
/limitbuy symbol:ROSE shares:20 price:13
/limitsell symbol:STMP shares:15 price:25
/alert symbol:CRAV type:above price:30
```

All three work 24/7 automatically!

## Next Steps

- [Commands Reference](/commands) - All commands explained
- [FAQ](/faq) - Common questions
- [Back to Home](/)

::: tip You're Now a GSC Pro!
Use these advanced tools to trade smarter, not harder. Automation and analytics give you an edge over manual traders!
:::
