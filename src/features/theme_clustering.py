def assign_themes(keywords):
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
        for key, theme in keyword_theme_map.items():
            if key in kw:
                assigned_themes.add(theme)

    return list(assigned_themes) if assigned_themes else ["Miscellaneous"]
