"""Team detection from roles and message tags."""
import re
from typing import Optional
from functools import lru_cache
import discord
import config


# Pre-compile regex pattern at module level for performance
_TAG_PATTERN = re.compile(r'\[([^\]]+)\]')

# Build reverse lookup map for O(1) role name → symbol lookups
_ROLE_TO_SYMBOL = {team['role_name']: symbol for symbol, team in config.TEAMS.items()}


def detect_team_from_message(message: discord.Message) -> Optional[str]:
    """Detect team from user roles or [TAG] in message content."""
    # Check roles first (non-bots only)
    if not message.author.bot:
        team_symbol = _detect_team_from_roles(message.author)
        if team_symbol:
            return team_symbol
    
    # Rule 2: Tag-based detection (fallback or for bot messages)
    team_symbol = _detect_team_from_tags(message.content)
    if team_symbol:
        return team_symbol
    
    # No team detected
    return None


def _detect_team_from_roles(member: discord.Member) -> Optional[str]:
    """Check if user has a team role."""
    if not isinstance(member, discord.Member):
        return None
    
    # Use reverse lookup map for O(1) performance
    for role in member.roles:
        if role.name in _ROLE_TO_SYMBOL:
            return _ROLE_TO_SYMBOL[role.name]
    
    return None


def _detect_team_from_tags(content: str) -> Optional[str]:
    """
    Detect team from message content tags.
    Returns the FIRST matching tag found in the message.
    """
    if not content:
        return None
    
    # Find all potential tags using pre-compiled pattern
    matches = _TAG_PATTERN.finditer(content)
    
    # Process tags in order of appearance
    for match in matches:
        tag = match.group(1).strip().upper()
        
        # Remove extra brackets from [[L]]
        if tag.startswith('[') and tag.endswith(']'):
            tag = tag[1:-1]
        
        # Check if this tag maps to a team (using cached lookup)
        symbol = _get_team_symbol_from_tag(tag)
        if symbol:
            return symbol
    
    return None


@lru_cache(maxsize=128)
def _get_team_symbol_from_tag(tag: str) -> Optional[str]:
    """Get team symbol from tag with LRU caching."""
    return config.TEAM_TAGS.get(tag)


@lru_cache(maxsize=32)
def get_team_name(symbol: str) -> Optional[str]:
    """Get the full team name from symbol."""
    team = config.TEAMS.get(symbol.upper())
    if team:
        return team['name']
    return None


@lru_cache(maxsize=32)
def get_team_info(symbol: str) -> Optional[dict]:
    """Get full team configuration."""
    return config.TEAMS.get(symbol.upper())


@lru_cache(maxsize=64)
def validate_symbol(symbol: str) -> bool:
    """Check if a symbol is valid."""
    return symbol.upper() in config.TEAMS


def normalize_symbol(symbol: str) -> str:
    """Normalize a symbol to uppercase."""
    return symbol.upper()
