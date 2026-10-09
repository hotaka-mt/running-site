from running_ocr.image_loader import select_img_path, load_image
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT
from running_ocr.ocr_engine import OCREngine
from running_ocr.pipeline import extract_running_data
from running_ocr.utils.image_window_manager import ImageWindowManager as IWM


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
    basic_info = extract_running_data(img, MI_FITNESS_LAYOUT, engine, sections=["basic"], window_manager=iwm)["basic"]
    
    display_fields = [
        ("datetime", "開始日時", lambda v: v.strftime("%Y/%m/%d %H:%M")),
        ("distance_km", "距離", lambda v: f"{v:.2f} km"),
        ("duration", "時間", lambda v: f"{v // 3600:02d}:{v % 3600 // 60:02d}:{v % 60:02d}"),
        ("active_kcal", "活動カロリー", lambda v: f"{v:,} kcal"),
        ("total_kcal", "総カロリー", lambda v: f"{v:,} kcal"),
        ("avg_pace", "平均ペース", lambda v: f"{v // 60}分{v % 60:02d}秒/km"),
        ("avg_bpm", "平均心拍数", lambda v: f"{v:,} bpm"),
        ("steps", "歩数", lambda v: f"{v:,} 歩"),
    ]
    print("\n抽出された基本情報")
    print("─" * 36)
    for key, label, formatter in display_fields:
        value = basic_info.get(key)
        formatted = formatter(value) if value is not None else "取得できませんでした"
        # 日本語ラベルの表示幅に合わせて値の開始位置を揃える。
        padding = " " * (12 - len(label) * 2)
        print(f"{label}{padding} : {formatted}")
    print("─" * 36)

    iwm.wait()


if __name__ == "__main__":
    main()
