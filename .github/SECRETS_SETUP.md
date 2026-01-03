# GitHub Secrets Setup

This document lists all secrets needed for CI/CD workflows.

## Required Secrets

### Deployment (deploy.yml)

1. **DEPLOY_HOST**
   - Description: SSH hostname or IP of your Ubuntu server
   - Example: `192.168.1.100` or `myserver.example.com`

2. **DEPLOY_USER**
   - Description: SSH username
   - Example: `ubuntu` or `gscbot`

3. **DEPLOY_KEY**
   - Description: Private SSH key for authentication
   - Generate: `ssh-keygen -t ed25519 -C "github-actions"`
   - Copy: `cat ~/.ssh/id_ed25519` (copy entire content including headers)

4. **DISCORD_TOKEN**
   - Description: Bot token from Discord Developer Portal
   - Get from: https://discord.com/developers/applications

5. **GUILD_ID**
   - Description: Discord server ID
   - Get: Enable Developer Mode in Discord → Right-click server → Copy ID

6. **ADMIN_ROLE_ID**
   - Description: Admin role ID for bot permissions
   - Get: Right-click role in Discord → Copy ID

### AI Review (ai-review.yml)

7. **GEMINI_API_KEY**
   - Description: Google Gemini API key for AI code reviews
   - Get from: https://aistudio.google.com/app/apikey
   - Free tier: 1500 requests/day

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter name (exactly as shown above) and value
5. Click **Add secret**
6. Repeat for all secrets

## Verify Secrets are Set

All secrets should show as configured (but values are hidden):
- ✅ DEPLOY_HOST
- ✅ DEPLOY_USER
- ✅ DEPLOY_KEY
- ✅ DISCORD_TOKEN
- ✅ GUILD_ID
- ✅ ADMIN_ROLE_ID
- ✅ GEMINI_API_KEY

## Testing

After adding secrets:

1. **Test deployment**: Push to main branch
   - Check Actions tab → Deploy workflow should succeed
   - SSH to server and verify bot restarted

2. **Test AI review**: Create a test PR
   - Check Actions tab → AI Code Review should run
   - PR should get automated comment from Gemini

## Troubleshooting

### Deployment fails with "permission denied"
- Check DEPLOY_KEY is the private key (starts with `-----BEGIN OPENSSH PRIVATE KEY-----`)
- Verify public key is in `~/.ssh/authorized_keys` on server

### AI review fails with "Failed to generate review"
- Check GEMINI_API_KEY is valid
- Visit https://aistudio.google.com/app/apikey to verify
- Ensure API key has access to `gemini-2.0-flash-exp` model

### Bot doesn't start after deployment
- Check DISCORD_TOKEN is correct
- Verify GUILD_ID and ADMIN_ROLE_ID are numeric IDs (not names)
- SSH to server and check logs: `journalctl -u gsc-bot -n 50`

## Security Best Practices

- ✅ Never commit secrets to git
- ✅ Use different tokens for dev/prod environments
- ✅ Rotate DISCORD_TOKEN if exposed
- ✅ Keep DEPLOY_KEY private (never share)
- ✅ Limit GEMINI_API_KEY permissions if possible

## Cost Tracking

| Secret | Service | Free Tier | Cost After |
|--------|---------|-----------|------------|
| DISCORD_TOKEN | Discord | Unlimited | Always free |
| GEMINI_API_KEY | Google AI | 1500 req/day | $0.35/1M tokens |
| GitHub Actions | GitHub | 2000 min/month | Free for public repos |

**Total monthly cost for hobby project**: $0 (stays within free tiers)
