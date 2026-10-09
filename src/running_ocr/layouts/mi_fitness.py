"""Mi Fitness のスクリーンショットの座標と、項目ごとの変換ルール。"""

# ペースの分・秒の区切りとして認識される文字を、パーサーの表記に揃える。
PACE_REPLACEMENTS = {"″": '"', "`": "'", "’": "'", "′": "'"}

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
    "bpm": {
        "crop": (940, 1710),
        # グラフ主体のスクリーンショットでは、書類向けの歪み補正を無効にする。
        "ocr_options": {
            "use_doc_unwarping": False,
        },
        "fields": {
            "avg_bpm": {"region": (0, 0, 198, 120), "parser": "int"},
            "max_bpm": {"region": (198, 0, None, 120), "parser": "int"},
            # グラフ内の目盛りは値として採用せず、区画としては画像全体を覆う。
            "chart": {"region": (0, 120, None, 365), "ignore": True},
            "warmup_seconds": {"region": (0, 365, None, 460), "parser": "duration"},
            "intensive_seconds": {"region": (0, 460, None, 540), "parser": "duration"},
            "aerobic_seconds": {"region": (0, 540, None, 595), "parser": "duration"},
            "anaerobic_seconds": {"region": (0, 595, None, 655), "parser": "duration"},
            "vo2max_seconds": {
                "region": (0, 655, None, None), "parser": "duration",
                # この行の時刻区切りがピリオドとして認識される場合に対応する。
                "replacements": {".": ":"},
            },
        },
    },
    "pace": {
        "crop": (1740, 2350),
        "ocr_options": {"use_doc_unwarping": False},
        "fields": {
            "avg_pace": {"region": (0, 0, 198, 120), "parser": "pace", "replacements": PACE_REPLACEMENTS},
            "best_pace": {"region": (198, 0, None, 120), "parser": "pace", "replacements": PACE_REPLACEMENTS},
            "chart": {"region": (0, 120, None, 370), "ignore": True},
            "lap_header": {"region": (0, 370, None, 475), "ignore": True},
            # 現在の画像は3行。最終行は1 km未満の区間も含む。
            "lap_1_pace": {"region": (0, 475, None, 512), "parser": "pace", "replacements": PACE_REPLACEMENTS},
            "lap_2_pace": {"region": (0, 512, None, 544), "parser": "pace", "replacements": PACE_REPLACEMENTS},
            "lap_3_pace": {"region": (0, 544, None, None), "parser": "pace", "replacements": PACE_REPLACEMENTS},
        },
    },
    "cadence": {
        "crop": (2350, 2745),
        "ocr_options": {"use_doc_unwarping": False},
        "fields": {
            "avg_cadence": {"region": (0, 0, 198, 135), "parser": "int"},
            "max_cadence": {"region": (198, 0, None, 135), "parser": "int"},
            "chart": {"region": (0, 135, None, None), "ignore": True},
        },
    },
    "stride": {
        "crop": (2750, 3145),
        "ocr_options": {"use_doc_unwarping": False},
        "fields": {
            "avg_stride_cm": {"region": (0, 0, 198, 130), "parser": "int"},
            "max_stride_cm": {"region": (198, 0, None, 130), "parser": "int"},
            "chart": {"region": (0, 130, None, None), "ignore": True},
        },
    },
    "effect": {
        "crop": (3150, 3545),
        "ocr_options": {"use_doc_unwarping": False},
        "fields": {
            "aerobic_effect": {"region": (0, 0, 198, 240), "parser": "float"},
            "anaerobic_effect": {"region": (198, 0, None, 240), "parser": "float"},
            "vo2max_ml_kg_min": {"region": (0, 240, 198, 325), "parser": "int", "unit": "ml/kg/min"},
            "training_load": {"region": (198, 240, None, 325), "parser": "int", "unit": "TL"},
            # 数字と「時間」が別々に認識されるため、数値を時間単位で保持する。
            "recovery_hours": {"region": (0, 325, None, None), "parser": "int"},
        },
    },
    "intensity": {
        "crop": (3560, 3680),
        "ocr_options": {"use_doc_unwarping": False},
        # 強度の値は数字ではないため、この領域では文字も処理対象にする。
        "numeric_only": False,
        "fields": {
            "heading": {"region": (0, 0, 280, None), "ignore": True},
            "intensity": {"region": (280, 0, 340, None), "parser": "text"},
            "icon": {"region": (340, 0, None, None), "ignore": True},
        },
    },
}
