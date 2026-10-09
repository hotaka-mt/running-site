"""Mi Fitness のスクリーンショットの座標と、項目ごとの変換ルール。"""
MI_FITNESS_LAYOUT = {
    "map": {"crop": (0, 605), "fields": {}},
    "basic": {
        "crop": (605, 915),
        "fields": {
            "distance_km": {"region": (0, 0, 208, 133), "parser": "float"},
            "datetime": {"region": (208, 0, None, 133), "parser": "datetime", "timezone": "Asia/Tokyo"},
            "duration": {"region": (0, 133, 122, 215), "parser": "duration"},
            "active_kcal": {"region": (122, 133, 246, 215), "parser": "int", "unit": "kcal"},
            "total_kcal": {"region": (246, 133, None, 215), "parser": "int", "unit": "kcal"},
            "avg_pace": {"region": (0, 215, 102, None), "parser": "pace"},
            "avg_bpm": {"region": (102, 215, 247, None), "parser": "int", "unit": "BPM"},
            "steps": {"region": (247, 215, None, None), "parser": "int"},
        },
    },
    "bpm": {"crop": (940, 1710), "fields": {}},
    "pace": {"crop": (1740, 2350), "fields": {}},
    "cadence": {"crop": (2350, 2745), "fields": {}},
    "stride": {"crop": (2750, 3145), "fields": {}},
    "effect": {"crop": (3150, 3545), "fields": {}},
    "intensity": {"crop": (3560, 3680), "fields": {}},
}
