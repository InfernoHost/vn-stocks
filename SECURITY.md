# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

We only support the latest version. Please update to the latest release to receive security updates.

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it privately:

### How to Report

1. **Email**: Send details to your-email@example.com (replace with your email)
2. **GitHub Security**: Use [GitHub Security Advisories](../../security/advisories/new)
3. **Discord**: DM the maintainer on Discord (if applicable)

### What to Include

Please include as much information as possible:

- **Type of vulnerability** (e.g., token leak, SQL injection, XSS)
- **Affected component** (file/function name)
- **Steps to reproduce** (detailed instructions)
- **Potential impact** (what an attacker could do)
- **Suggested fix** (if you have one)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: 1 month

## Security Best Practices

When contributing to this project:

### Never Commit Secrets
- ❌ API keys, tokens, passwords
- ❌ Private keys, certificates
- ❌ Database credentials
- ✅ Use environment variables
- ✅ Use GitHub Secrets for CI/CD

### Code Security
- ✅ Validate all user input
- ✅ Use parameterized queries (we use SQLite with aiosqlite)
- ✅ Keep dependencies updated
- ✅ Review Dependabot PRs promptly

### Discord Bot Security
- ✅ Use role-based permissions
- ✅ Validate command permissions
- ✅ Rate limit user actions
- ✅ Sanitize user-provided data

## Automatic Security Checks

This repository has automated security scanning:

- **CodeQL** - Runs on every PR and weekly
- **Dependabot** - Scans for vulnerable dependencies
- **Bandit** - Python security linter on PRs
- **Safety** - Dependency vulnerability checker
- **Secret scanning** - Detects leaked credentials

Check the [Security tab](../../security) for any alerts.

## Known Security Considerations

### Discord Token Protection
- Token must be in `.env` file (gitignored)
- Never log the token
- Rotate immediately if exposed

### Database Security
- SQLite database is local only
- No remote access configured
- Backup regularly

### Market Data
- Price manipulation through message spam is rate-limited
- Activity decay prevents sustained manipulation
- Admin commands are role-protected

## Security Updates

We announce security updates through:
- GitHub Security Advisories
- Release notes
- Discord server announcements

## Attribution

We thank security researchers who responsibly disclose vulnerabilities. With your permission, we'll credit you in:
- Release notes
- Security advisories
- README acknowledgments

## Questions?

For security-related questions (not vulnerabilities), open a [GitHub Discussion](../../discussions/new?category=security).
