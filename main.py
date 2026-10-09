from running_ocr.image_loader import select_img_path, load_image
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT
from running_ocr.ocr_engine import OCREngine
from running_ocr.pipeline import extract_running_data
from running_ocr.utils.image_window_manager import ImageWindowManager as IWM


def display_info(title, info, fields):
    """抽出結果を、項目ごとの表示形式で端末に出力する。"""
    print(f"\n{title}")
    print("─" * 36)
    label_width = max(len(label) * 2 for _, label, _ in fields)
    for key, label, formatter in fields:
        value = info.get(key)
        formatted = formatter(value) if value is not None else "取得できませんでした"
        # 日本語ラベルの表示幅に合わせて値の開始位置を揃える。
        padding = " " * (label_width - len(label) * 2)
        print(f"{label}{padding} : {formatted}")
    print("─" * 36)


def main():
    # 画像の選択
    img_path = select_img_path()
    if img_path is None:
        return

    # 画像の読み込み
    img = load_image(img_path)
    if img is None:
        return

    # ウィンドウマネージャ
    iwm = IWM()

    engine = OCREngine()
    running_data = extract_running_data(img, MI_FITNESS_LAYOUT, engine, window_manager=iwm)

    format_pace = lambda value: f"{value // 60}分{value % 60:02d}秒/km"
    display_fields = [
        ("datetime", "開始日時", lambda v: v.strftime("%Y/%m/%d %H:%M")),
        ("distance_km", "距離", lambda v: f"{v:.2f} km"),
        ("duration", "時間", lambda v: f"{v // 3600:02d}:{v % 3600 // 60:02d}:{v % 60:02d}"),
        ("active_kcal", "活動カロリー", lambda v: f"{v:,} kcal"),
        ("total_kcal", "総カロリー", lambda v: f"{v:,} kcal"),
        ("avg_pace", "平均ペース", format_pace),
        ("avg_bpm", "平均心拍数", lambda v: f"{v:,} bpm"),
        ("steps", "歩数", lambda v: f"{v:,} 歩"),
    ]
    display_info("抽出された基本情報", running_data["basic"], display_fields)
    format_duration = lambda value: f"{value // 3600:02d}:{value % 3600 // 60:02d}:{value % 60:02d}"
    bpm_fields = [
        ("avg_bpm", "平均心拍数", lambda value: f"{value:,} bpm"),
        ("max_bpm", "最大心拍数", lambda value: f"{value:,} bpm"),
        ("warmup_seconds", "ウォームアップ", format_duration),
        ("intensive_seconds", "インテンシブ", format_duration),
        ("aerobic_seconds", "有酸素", format_duration),
        ("anaerobic_seconds", "無酸素", format_duration),
        ("vo2max_seconds", "最大酸素摂取量", format_duration),
    ]
    display_info("抽出された心拍数情報", running_data["bpm"], bpm_fields)

    # 各領域の値を、保存している単位に合わせて表示する。
    other_fields = [
        ("pace", "ペース情報", [
            ("avg_pace", "平均ペース", format_pace),
            ("best_pace", "最高ペース", format_pace),
            ("lap_1_pace", "１区間目", format_pace),
            ("lap_2_pace", "２区間目", format_pace),
            ("lap_3_pace", "３区間目", format_pace),
        ]),
        ("cadence", "ケイデンス情報", [
            ("avg_cadence", "平均ケイデンス", lambda value: f"{value:,} 回/分"),
            ("max_cadence", "最高ケイデンス", lambda value: f"{value:,} 回/分"),
        ]),
        ("stride", "ストライド情報", [
            ("avg_stride_cm", "平均ストライド", lambda value: f"{value:,} cm"),
            ("max_stride_cm", "最大ストライド", lambda value: f"{value:,} cm"),
        ]),
        ("effect", "トレーニング効果", [
            ("aerobic_effect", "有酸素効果", lambda value: f"{value:.1f}"),
            ("anaerobic_effect", "無酸素効果", lambda value: f"{value:.1f}"),
            ("vo2max_ml_kg_min", "最大酸素摂取量", lambda value: f"{value:,} ml/kg/min"),
            ("training_load", "トレーニング負荷", lambda value: f"{value:,} TL"),
            ("recovery_hours", "回復時間", lambda value: f"{value:,} 時間"),
        ]),
        ("intensity", "トレーニング強度", [
            ("intensity", "強度", str),
        ]),
    ]
    for section, title, fields in other_fields:
        display_info(f"抽出された{title}", running_data[section], fields)

    iwm.wait()


if __name__ == "__main__":
    main()
