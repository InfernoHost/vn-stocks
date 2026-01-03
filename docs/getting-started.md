# Getting Started with GSC 🚀

This guide will walk you through everything you need to know to start trading in the Gearfall Stock Exchange.

## Step 1: Register Your Account

Before you can trade, you need to create an account.

**/register**

Creates your trading account and gives you 10 Cogs starting capital

**What happens:**
- You receive **10 Cogs** (640 Spurs) in your wallet
- A portfolio is created to track your holdings
- You can now buy/sell stocks and use all features

::: warning Important
You can only register once! Make sure you're using the right Discord account.
:::

## Step 2: Check Your Balance

See how much money you have available to trade.

**/balance**

Shows your current cash balance and total portfolio value

**Example output:**
```
💰 Balance: 10 Cogs
📊 Portfolio Value: 0 Cogs
💎 Total Worth: 10 Cogs
```

## Step 3: View the Market

Before buying, check which stocks are available and their current prices.

**/market**

Lists all available stocks with current prices and 24h changes

**Example output:**
```
📈 Current Market Prices
━━━━━━━━━━━━━━━━━━━━
STMP: 20.45 Cogs (+2.3%)
ROSE: 14.87 Cogs (-0.5%)
VIOL: 19.12 Cogs (+5.1%)
POT: 11.95 Cogs (-1.2%)
CRAV: 26.33 Cogs (+3.8%)
VOC: 15.78 Cogs (+0.9%)
```

::: tip
Green percentages mean the stock went up, red means it went down!
:::

## Step 4: Check a Specific Stock

Get detailed information about a single stock before buying.

**/stock symbol:STMP**

Shows current price, 24h change, volatility, and price history

**What you'll see:**
- Current price in Cogs
- 24-hour price change (%)
- Volatility rating
- Recent price history
- Market cap

## Step 5: Make Your First Trade

### Buying Stocks

**/buy symbol:STMP shares:5**

Buys 5 shares of STMP at current market price

**What happens:**
1. Bot checks if you have enough money
2. Calculates total cost (price × shares)
3. Deducts money from your balance
4. Adds shares to your portfolio
5. Records transaction in your history

**Example:**
```
You bought 5 shares of STMP
Price: 20.45 Cogs per share
Total Cost: 102.25 Cogs
New Balance: 7.75 Cogs remaining
```

### Selling Stocks

**/sell symbol:STMP shares:3**

Sells 3 shares of STMP at current market price

**What happens:**
1. Bot checks if you own enough shares
2. Calculates total proceeds (price × shares)
3. Removes shares from your portfolio
4. Adds money to your balance
5. Records transaction in your history

**Example:**
```
You sold 3 shares of STMP
Price: 21.80 Cogs per share
Total Proceeds: 65.40 Cogs
Profit: +4.05 Cogs (+6.6%)
New Balance: 73.15 Cogs
```

::: tip Success!
If you sold for more than you bought, you made money!
:::

## Step 6: Check Your Portfolio

See all your current holdings and how they're performing.

**/portfolio**

Shows all your stocks with current values and P/L

**Example output:**
```
📊 Your Portfolio
━━━━━━━━━━━━━━━━━━━━

STMP: 2 shares
  Value: 43.60 Cogs
  P/L: +2.70 Cogs (+6.6%)

Cash: 73.15 Cogs
Total Worth: 116.75 Cogs
Overall P/L: +16.75 Cogs (+16.8%)
```

You also get a pie chart showing your asset allocation!

## Step 7: View Price Charts

See how stock prices have changed over time.

**/graph symbol:STMP**

Shows a live-updating TradingView style price chart

**Features:**
- Updates every 30 seconds automatically
- Shows last 24 hours of price data
- TradingView dark theme styling
- Stop/Start buttons to control updates

::: tip Pro Tip
Use `/candlestick symbol:STMP` for OHLC candlestick charts showing price patterns!
:::

## Common Mistakes to Avoid

### 1. Spending All Your Money at Once
**Problem:** You buy everything with your 10 Cogs, then a better opportunity appears

**Solution:** Keep some cash in reserve for new opportunities

### 2. Panic Selling
**Problem:** Stock drops 2% and you sell immediately, missing the recovery

**Solution:** Markets fluctuate! Hold through small dips unless you have a reason to sell

### 3. Ignoring Activity
**Problem:** Buying a stock when the team is inactive

**Solution:** Check team activity in Discord - active teams = rising prices

### 4. Not Setting Alerts
**Problem:** Missing the perfect sell price while you're asleep

**Solution:** Use `/alert` to get DM'd when stocks hit your target price

### 5. Forgetting to Check Charts
**Problem:** Buying at a peak without seeing the trend

**Solution:** Always check `/graph` or `/candlestick` before big trades

## What's Next?

Now that you know the basics, level up your trading:

- [Trading Guide](/trading) - Learn strategies and techniques
- [Advanced Features](/advanced) - Limit orders, alerts, and more
- [Commands Reference](/commands) - Complete command list
- [FAQ](/faq) - Common questions answered

::: tip Ready to Trade!
You now have everything you need to start making money in GSC. Head to Discord and type `/register` to begin!
:::
