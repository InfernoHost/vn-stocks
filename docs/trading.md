# Trading Guide 📈

Master the art of trading in GSC with proven strategies, tips, and techniques.

## Understanding Price Movement

### What Makes Prices Go Up? 📊

**Team Activity (40% impact)**
- Every message from team members adds to activity score
- Activity score decays by 5% every 3 minutes
- High activity = strong upward pressure on price

**Random Volatility (30% impact)**
- Each stock has a volatility rating (Low/Medium/High)
- Higher volatility = bigger price swings
- Creates opportunities but also risks

**Momentum (20% impact)**
- Stocks trending up tend to keep going up
- Stocks trending down tend to keep going down
- Momentum persists but eventually reverses

**Mean Reversion (10% impact)**
- Prices naturally want to return to "normal"
- Extreme highs get pulled down
- Extreme lows get pulled up

### Price Update Cycle ⏱️

Market updates happen **every 3 minutes**:

1. Bot calculates activity scores for each team
2. Applies random volatility based on stock settings
3. Factors in momentum from recent trends
4. Checks for mean reversion opportunities
5. Updates all prices simultaneously
6. Executes any triggered limit orders

## Basic Trading Strategies

### 1. Activity Trading (Beginner) 🎯

**Concept:** Buy stocks of teams that are chatting a lot

**How it works:**
- Monitor Discord channels
- When you see a team getting super active, buy their stock
- Sell after a few price updates when activity dies down

**Example:**
```
11:00 - VIOL team starts big discussion (20+ messages)
11:03 - Price updates: VIOL +5.2% (activity impact)
11:06 - Price updates: VIOL +3.1% (activity continues)
11:09 - Activity slows, you sell for +8% profit
```

::: tip Best For
New traders who want quick, observable results
:::

### 2. Volatility Trading (Intermediate) 📊

**Concept:** Trade high-volatility stocks for bigger gains

**How it works:**
- Focus on VIOL and CRAV (high volatility stocks)
- Buy on dips (when price drops sharply)
- Sell on spikes (when price jumps up)
- Accept higher risk for higher reward

**Example:**
```
Day 1: CRAV drops from 28 → 24 Cogs (-14%)
       You buy 10 shares at 24 Cogs
Day 2: Random volatility spike: 24 → 29 Cogs (+21%)
       You sell for +50 Cogs profit
```

::: warning Risk
High volatility can go against you just as easily!
:::

### 3. Momentum Trading (Intermediate) 🚀

**Concept:** "The trend is your friend" - ride the wave

**How it works:**
- Use `/graph` to spot upward trends
- Buy stocks showing consistent growth
- Hold as long as the trend continues
- Sell when momentum reverses

**Example:**
```
Week 1: ROSE trending up steadily
        14 → 15 → 16.5 → 17.8 Cogs
        You buy at 16.5 Cogs
Week 2: Trend continues to 19.2 Cogs
        You sell for +16% profit
```

::: tip
Use `/candlestick` to see trend strength visually
:::

### 4. Diversification (Defensive) 🛡️

**Concept:** Don't put all your eggs in one basket

**How it works:**
- Split money across 3-4 different stocks
- Mix high and low volatility stocks
- Reduces risk of total loss
- Steadier returns over time

**Example portfolio:**
```
30% STMP (medium volatility, active team)
30% ROSE (low volatility, steady)
20% VIOL (high volatility, potential big gains)
20% Cash (for opportunities)
```

::: tip Best For
Risk-averse traders who want stable growth
:::

## Advanced Techniques

### Using Limit Orders ⚡

Instead of watching charts 24/7, set automatic buy/sell orders.

**Buy Limit Example:**
```
STMP currently at 22 Cogs (too expensive)
Set buy limit at 20 Cogs for 10 shares
Go to sleep
Price drops to 19.8 Cogs overnight
Order executes automatically
You wake up owning 10 shares!
```

**Sell Limit Example:**
```
You own 15 VIOL at 18 Cogs
Set sell limit at 22 Cogs (20% profit)
Price spikes to 22.5 Cogs during the day
Order executes automatically at 22 Cogs
Profit secured without watching!
```

See the [Advanced Features guide](/advanced) for details!

### Using Price Alerts 🔔

Get notified when prices hit your targets.

**Setup:**
```
/alert symbol:CRAV type:above price:28
```

**What happens:**
- You go about your day
- CRAV price rises to 28.5 Cogs
- Bot DMs you immediately
- You check the chart and decide to buy/sell
- No need to constantly refresh!

## Risk Management

### Position Sizing 📏

**Rule of thumb:**
- Never invest more than 30% in one stock
- Keep 10-20% cash for opportunities
- Start small (5-10% per position) as beginner

**Example:**
```
Starting capital: 10 Cogs

Good allocation:
- 2 Cogs in STMP (20%)
- 2 Cogs in ROSE (20%)
- 2 Cogs in VOC (20%)
- 1.5 Cogs in POT (15%)
- 2.5 Cogs cash (25%)
```

### Stop Losses (Mental) 🛑

Decide in advance when to cut losses:

**Example rule:**
"If any position drops more than 20%, I sell immediately"

**Why this helps:**
- Prevents holding losers too long
- Protects capital for better trades
- Removes emotion from decisions

## Common Trading Mistakes

### ❌ Revenge Trading
**Mistake:** Losing money then immediately making risky trades to "win it back"

**Solution:** Take a break after losses. Come back with clear head.

### ❌ FOMO (Fear of Missing Out)
**Mistake:** Buying a stock because it already went up 30%

**Solution:** Wait for pullbacks. There's always another opportunity.

### ❌ Overtrading
**Mistake:** Making 10+ trades per day chasing every small move

**Solution:** Quality over quantity. Wait for high-confidence setups.

## Quick Strategy Reference

| Strategy | Risk Level | Time Horizon | Best For |
|----------|------------|--------------|----------|
| Activity Trading | Low | Minutes-Hours | Beginners |
| Volatility Trading | High | Hours-Days | Risk-takers |
| Momentum Trading | Medium | Days-Weeks | Trend followers |
| Diversification | Low | Weeks-Months | Defensive |

## Next Steps

- [Advanced Features](/advanced) - Limit orders, alerts, and tools
- [Commands Reference](/commands) - All available commands
- [FAQ](/faq) - Common questions answered

::: tip Ready to Trade Like a Pro?
Apply these strategies in Discord and track your results over time. The best traders learn from both wins and losses!
:::
