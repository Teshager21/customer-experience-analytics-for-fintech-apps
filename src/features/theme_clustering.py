# src/features/theme_assignment.py

from typing import List
import logging

logger = logging.getLogger(__name__)


def assign_themes(keywords: List[str]) -> List[str]:
    """
    Assigns user-provided keywords to pre-defined themes using substring matching.

    Args:
        keywords (List[str]): A list of keywords extracted from text data.

    Returns:
        List[str]: A list of unique themes matched from the keywords,
                   or ['Miscellaneous'] if no match is found.
    """
    keyword_theme_map = {
        "login": "Account Access Issues",
        "password": "Account Access Issues",
        "crash": "Reliability",
        "slow": "Transaction Performance",
        "support": "Customer Support",
        "interface": "User Experience",
        "design": "User Experience",
        "feature": "Feature Requests",
        "update": "Feature Requests",
    }

    assigned_themes = set()
    for kw in keywords:
        kw_lower = kw.lower()
        for key, theme in keyword_theme_map.items():
            if key in kw_lower:
                assigned_themes.add(theme)
                logger.debug(f"Matched '{kw}' to theme '{theme}'")

    if not assigned_themes:
        logger.debug("No matches found. Assigning theme: 'Miscellaneous'")
        return ["Miscellaneous"]

    return sorted(assigned_themes)
