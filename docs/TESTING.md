# Testing Guide

## Manual Testing Checklist

Before submitting a PR or deploying, test these scenarios:

### Setup & Registration
- [ ] Bot starts without errors
- [ ] `/register` creates new account
- [ ] `/register` prevents duplicate registration
- [ ] Starting balance is correct (10 Cogs)

### Balance & Portfolio
- [ ] `/balance` shows current balance
- [ ] `/balance` shows error if not registered
- [ ] `/portfolio` shows empty state for new users
- [ ] `/portfolio` shows holdings after purchases

### Market Commands
- [ ] `/market` displays all stocks
- [ ] `/market` shows price changes
- [ ] `/stock <symbol>` shows individual stock details
- [ ] Invalid symbols show error messages

### Trading
- [ ] `/buy` purchases shares successfully
- [ ] `/buy` deducts correct amount from balance
- [ ] `/buy` prevents purchase with insufficient funds
- [ ] `/buy` rejects negative amounts
- [ ] `/buy` rejects invalid symbols
- [ ] `/sell` sells shares successfully
- [ ] `/sell` adds correct amount to balance
- [ ] `/sell` prevents selling more than owned
- [ ] `/sell` rejects negative amounts
- [ ] Portfolio updates after trades

### Market Mechanics
- [ ] Prices update every 3 minutes
- [ ] Messages with team roles increase activity
- [ ] Messages with [TAGS] increase activity
- [ ] Message cooldown prevents spam (60s)
- [ ] Activity scores decay over time
- [ ] Prices don't go below 1 Spur

### Graphs
- [ ] `/graph <symbol>` generates price chart
- [ ] Graph shows correct time period
- [ ] Graph displays price movements
- [ ] Image loads properly in Discord

### Admin Commands
- [ ] `/give` adds currency to users
- [ ] `/take` removes currency from users
- [ ] `/setprice` changes stock prices
- [ ] `/resetmarket` resets all prices
- [ ] Admin commands require admin role
- [ ] Non-admins see permission error

### Error Handling
- [ ] Invalid commands show helpful errors
- [ ] Database errors don't crash bot
- [ ] Network errors are handled gracefully
- [ ] All error messages are ephemeral

### Edge Cases
- [ ] Buying 0 shares shows error
- [ ] Selling 0 shares shows error
- [ ] Extremely large numbers are handled
- [ ] Special characters in inputs don't break bot
- [ ] Bot handles being offline/restarting

## Testing in Development

### Local Testing

```bash
# Set up test environment
cp .env .env.test
# Edit .env.test with test server credentials

# Run bot locally
python bot.py

# Test in your Discord test server
```

### Test Data Setup

```python
# In Python console or test script
import asyncio
import database

async def setup_test_data():
    await database.init_db()
    
    # Create test users
    await database.register_player(123456789)  # Test user 1
    await database.register_player(987654321)  # Test user 2
    
    # Give test balance
    await database.update_balance(123456789, 10000 * 64)  # 10k Cogs
    
    print("Test data created!")

asyncio.run(setup_test_data())
```

## Automated Testing

### Run Validation Locally

```bash
# Install dev dependencies
pip install flake8 pylint

# Check code style
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check imports
python -c "import bot, config, database, market, team_detection, utils"

# Validate config
python -c "import config; assert len(config.TEAMS) > 0"
```

### Test Database Operations

```python
import asyncio
import database
import os

async def test_database():
    # Use test DB
    database.config.DB_PATH = 'test.db'
    
    try:
        # Test init
        await database.init_db()
        print("✓ Database created")
        
        # Test registration
        success = await database.register_player(123)
        assert success
        print("✓ Player registration works")
        
        # Test balance
        player = await database.get_player(123)
        assert player is not None
        print("✓ Player retrieval works")
        
        # Test duplicate registration
        success = await database.register_player(123)
        assert not success
        print("✓ Duplicate prevention works")
        
        print("\nAll tests passed!")
    finally:
        if os.path.exists('test.db'):
            os.remove('test.db')

asyncio.run(test_database())
```

## Performance Testing

### Load Testing

Test with multiple concurrent users:

```python
# Simulate 10 users trading
for i in range(10):
    # Use /buy and /sell commands rapidly
    # Check response times
    # Monitor memory usage
```

### Memory Monitoring

```bash
# Check bot memory usage
ps aux | grep python

# Monitor over time
watch -n 5 'ps aux | grep python'
```

## Common Test Scenarios

### Scenario 1: New Player Flow
1. New user joins server
2. Runs `/register`
3. Runs `/market` to see stocks
4. Runs `/buy STMP 5`
5. Runs `/portfolio` to verify
6. Messages in team channel
7. Waits for price update
8. Runs `/sell STMP 2`

### Scenario 2: Admin Management
1. Admin runs `/give @user 100`
2. User checks `/balance`
3. Admin runs `/setprice ROSE 200`
4. Users check `/market`
5. Admin runs `/resetmarket`
6. Prices return to starting values

### Scenario 3: Market Activity
1. Multiple team members send messages
2. Wait for update cycle (3 min)
3. Check if prices changed
4. Verify activity decay works
5. Test cooldown prevents spam

## Regression Testing

After major changes, verify:
- [ ] Existing player data intact
- [ ] Old commands still work
- [ ] Config changes applied correctly
- [ ] No breaking changes to database schema
- [ ] Market data preserved

## Deployment Testing

After deploying to server:
- [ ] Bot comes online
- [ ] Commands sync properly
- [ ] Database accessible
- [ ] Market simulator running
- [ ] Logs show no errors
- [ ] Existing users can trade

```bash
# Check bot status
sudo systemctl status gsc-bot

# View live logs
sudo journalctl -u gsc-bot -f

# Test command sync
# Run /market in Discord
```

## Bug Report Template

When you find a bug:

```
## Bug Description
[Clear description of what went wrong]

## Steps to Reproduce
1. Run /command
2. Do X
3. Error occurs

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Environment
- Bot version: [commit hash]
- Server: [test/production]
- Python version: [3.8/3.9/etc]

## Screenshots/Logs
[Include relevant screenshots or log output]

## Additional Context
[Any other relevant information]
```

## Test Coverage Goals

Aim for:
- ✅ All user commands tested
- ✅ All admin commands tested
- ✅ All error cases handled
- ✅ Database operations verified
- ✅ Market mechanics working
- ✅ No unhandled exceptions
