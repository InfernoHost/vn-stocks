# Code Review Guidelines

## For Reviewers

### What to Check

#### 1. Security
- [ ] No hardcoded tokens, passwords, or API keys
- [ ] User input is validated and sanitized
- [ ] SQL queries use parameterized statements (already handled by aiosqlite)
- [ ] File paths are validated

#### 2. Functionality
- [ ] Code does what the PR description claims
- [ ] Edge cases are handled
- [ ] Error messages are clear and helpful
- [ ] Commands respond appropriately to invalid input

#### 3. Code Quality
- [ ] Follows PEP 8 style guidelines
- [ ] Functions are focused and not too long
- [ ] Variable names are descriptive
- [ ] No commented-out code blocks
- [ ] Docstrings exist for new functions

#### 4. Project Conventions
- [ ] Currency stored as Spurs internally
- [ ] User-facing output uses `utils.spurs_to_cogs_display()`
- [ ] Database operations are async
- [ ] Commands use `discord.Embed` for responses
- [ ] Error messages use ephemeral messages
- [ ] Admin commands have proper permission checks

#### 5. Testing
- [ ] PR author tested the changes
- [ ] No obvious bugs or typos
- [ ] Database migrations handled if schema changed

### Common Issues to Watch For

**Currency Handling**
```python
# ❌ BAD: Displaying raw Spurs
await interaction.response.send_message(f"Balance: {balance}")

# ✅ GOOD: Convert to Cogs display
balance_str = utils.spurs_to_cogs_display(balance)
await interaction.response.send_message(f"Balance: {balance_str}")
```

**Error Handling**
```python
# ❌ BAD: Generic error
await interaction.response.send_message("Error!")

# ✅ GOOD: Specific error message
await interaction.response.send_message(
    "❌ You don't have enough Cogs for this purchase!",
    ephemeral=True
)
```

**Admin Commands**
```python
# ❌ BAD: No permission check
@app_commands.command(name="give")
async def give(self, interaction, user, amount):
    ...

# ✅ GOOD: Permission check decorator
@app_commands.command(name="give")
@app_commands.checks.has_role(config.ADMIN_ROLE_ID)
async def give(self, interaction, user, amount):
    ...
```

**Async Operations**
```python
# ❌ BAD: Forgetting await
price = market.market.get_price(symbol)

# ✅ GOOD: Await async calls
price = await market.market.get_price(symbol)
```

### Review Process

1. **Read the PR description** - Understand what's being changed and why
2. **Check the files changed** - Review each file modification
3. **Test locally if needed** - For major changes, pull and test
4. **Leave constructive feedback** - Be specific and helpful
5. **Approve or request changes** - Clear decision with reasoning

### Giving Feedback

**Good feedback:**
- "This function is getting long. Consider extracting the database logic into a helper function."
- "Great addition! Could you add a docstring explaining what `factor` represents?"
- "We should validate that `shares` is positive before the database call to fail fast."

**Avoid:**
- "This is wrong." (Be specific about what and why)
- "Just use X instead." (Explain the reasoning)
- Nitpicking style if it's consistent with existing code

## For Contributors

### Before Requesting Review

- [ ] All validation checks pass
- [ ] You've tested the changes locally
- [ ] No merge conflicts with main branch
- [ ] PR description clearly explains changes
- [ ] Commits have meaningful messages

### Responding to Review Feedback

- Read all feedback before responding
- Ask questions if something is unclear
- Make requested changes in new commits (don't force push)
- Mark conversations as resolved once addressed
- Thank reviewers for their time

### Common Mistakes to Avoid

1. **Not testing thoroughly** - Always run the bot locally
2. **Ignoring validation errors** - Fix all CI failures before review
3. **Force pushing** - Use new commits during review process
4. **Taking feedback personally** - Reviews improve code quality
5. **Submitting huge PRs** - Keep changes focused and manageable

## Approval Process

- **1 approval required** for simple changes (docs, minor fixes)
- **2 approvals required** for major features or architecture changes
- **Admin approval required** for config changes or admin commands

After approval:
1. Squash and merge for feature branches
2. Merge commit for important milestones
3. Delete branch after merging
