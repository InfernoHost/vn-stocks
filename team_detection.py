"""Team detection from roles and message tags."""
import re
from typing import Optional
import discord
import config


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
    
    # Check roles in order
    for role in member.roles:
        for symbol, team in config.TEAMS.items():
            if role.name == team['role_name']:
                return symbol
    
    return None


def _detect_team_from_tags(content: str) -> Optional[str]:
    """
    Detect team from message content tags.
    Returns the FIRST matching tag found in the message.
    """
    if not content:
        return None
    
    # Find all potential tags in the message
    # Match patterns like [TAG] (case-insensitive)
    tag_pattern = r'\[([^\]]+)\]'
    matches = re.finditer(tag_pattern, content)
    
    # Process tags in order of appearance
    for match in matches:
        tag = match.group(1).strip().upper()
        
        # Remove extra brackets from [[L]]
        if tag.startswith('[') and tag.endswith(']'):
            tag = tag[1:-1]
        
        # Check if this tag maps to a team
        if tag in config.TEAM_TAGS:
            return config.TEAM_TAGS[tag]
    
    return None


def get_team_name(symbol: str) -> Optional[str]:
    """Get the full team name from symbol."""
    team = config.TEAMS.get(symbol)
    if team:
        return team['name']
    return None


def get_team_info(symbol: str) -> Optional[dict]:
    """Get full team configuration."""
    return config.TEAMS.get(symbol)


def validate_symbol(symbol: str) -> bool:
    """Check if a symbol is valid."""
    return symbol.upper() in config.TEAMS


def normalize_symbol(symbol: str) -> str:
    """Normalize a symbol to uppercase."""
    return symbol.upper()
