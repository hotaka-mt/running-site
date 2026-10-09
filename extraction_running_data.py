import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import cv2 as cv
from image_window_manager import ImageWindowManager as IWM
from paddleocr import PaddleOCR

def select_img_path(folder_path="img/"):
    # フォルダが存在するか確認
    if not os.path.exists(folder_path):
        print(f"フォルダ '{folder_path}' が存在しません。")
        return None

    # ディレクトリ内のjpgファイルを取得
    img_files = [f for f in os.listdir(folder_path) if f.endswith((".jpg"))]
    if not img_files:
        print(f"フォルダ '{folder_path}' にjpgファイルが存在しません。")
        return None

    # 取得した画像ファイルのパスを表示
    for index, img_file in enumerate(img_files):
        print(f"画像{index+1}: {img_file}")

    # ユーザーに画像番号を入力させる
    while True:
        try:
            selected_index = int(input("画像番号を入力してください: ")) - 1
        except ValueError:
            print("無効な入力です。数字を入力してください。")
            continue

        if 0 <= selected_index < len(img_files):
            return os.path.join(folder_path, img_files[selected_index])

        print(f"1〜{len(img_files)}の番号を入力してください。")


def load_image(img_path):
    # 画像を読み込む
    img = cv.imread(img_path)
    if img is None:
        print("画像が読み込めませんでした。パスを確認してください。")
        return None
    return img

def trimming_image(running_img):
    # 画像をトリミングしてディクショナリにまとめる
    img_dict = {
        "map_img": running_img[:605, :],  # ランニングコースのマップ画像
        "basic_img": running_img[605:915, :],  # ランニング基本情報
        "bpm_img": running_img[940:1710, :],  # ランニング心拍数情報
        "pace_img": running_img[1740:2350, :],  # ランニングペース情報
        "cadence_img": running_img[2350:2745, :],  # ランニングケイデンス情報
        "stride_img": running_img[2750:3145, :],  # ランニングストライド情報
        "effect_img": running_img[3150:3545, :],  # ランニング効果情報
        "intensity_img": running_img[3560:3680, :],  # ランニング強度情報
    }

    return img_dict

def extract_basic_data(basic_img, iwm=None):
    # OCR の実行
    ocr = PaddleOCR(lang="japan", use_textline_orientation=True)
    ocr_result = ocr.predict(basic_img)

    # 結果の表示
    basic_data = []
    ocr_img = basic_img.copy()
    for res in ocr_result:
        for text, score, box in zip(res["rec_texts"], res["rec_scores"], res["rec_boxes"]):
            text = text.strip()
            # 数字が1文字でも含まれる結果を表示する。
            if re.search(r"\d", text) is None:
                continue

            x_min, y_min, x_max, y_max = map(int, box)
            center = ((x_min + x_max) // 2, (y_min + y_max) // 2)

            basic_data.append({
                "text": text,
                "score": score,
                "center": center
            })

            # print(f"テキスト: {text}, 信頼度: {score:.2f}, 矩形: ({x_min}, {y_min}), ({x_max}, {y_max}), 中心座標: {center}")

            if iwm:
                top_left = (x_min, y_min)
                bottom_right = (x_max, y_max)

                cv.rectangle(ocr_img, top_left, bottom_right, (0, 255, 0), 1)
                cv.putText(ocr_img, f"{text} ({score:.2f})", top_left, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 画像を表示する場合
    if iwm:
        iwm.show_image("ocr_img", ocr_img)

    return basic_data

def create_regions(image_shape):
    """固定レイアウトを、重複しない半開区間の8区画に分割する。"""
    height, width = image_shape[:2]

    return {
        "distance_km": (0, 0, 208, 133),
        "datetime": (208, 0, width, 133),
        "duration": (0, 133, 122, 215),
        "active_kcal": (122, 133, 246, 215),
        "total_kcal": (246, 133, width, 215),
        "avg_pace": (0, 215, 102, height),
        "avg_bpm": (102, 215, 247, height),
        "steps": (247, 215, width, height),
    }


def get_region_key(center_x, center_y, regions):
    for key, (x1, y1, x2, y2) in regions.items():
        if x1 <= center_x < x2 and y1 <= center_y < y2:
            return key
    return None


def parse_basic_value(key, text):
    """OCR文字列を項目の型・単位に変換する。変換できなければNone。"""
    if text is None:
        return None
    text = text.strip()
    try:
        if key == "distance_km":
            if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
                return float(text)
        elif key == "datetime":
            # 日付と時刻の間に空白がないOCR結果にも対応する。
            match = re.fullmatch(
                r"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})\s*([0-9]{2}):([0-9]{2})",
                text,
            )
            if match:
                return datetime(*map(int, match.groups()), tzinfo=ZoneInfo("Asia/Tokyo"))
        elif key == "duration":
            match = re.fullmatch(r"([0-9]+):([0-9]{2}):([0-9]{2})", text)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                if minutes < 60 and seconds < 60:
                    return hours * 3600 + minutes * 60 + seconds
        elif key == "avg_pace":
            match = re.fullmatch(r"([0-9]+)'([0-9]{2})\"", text)
            if match:
                minutes, seconds = map(int, match.groups())
                if seconds < 60:
                    return minutes * 60 + seconds
        else:
            patterns = {
                "active_kcal": r"([0-9]+)\s*kcal",
                "total_kcal": r"([0-9]+)\s*kcal",
                "avg_bpm": r"([0-9]+)\s*BPM",
                "steps": r"([0-9]+)",
            }
            pattern = patterns.get(key)
            if pattern:
                match = re.fullmatch(pattern, text, flags=re.IGNORECASE)
                if match:
                    return int(match.group(1))
    except ValueError:
        # 存在しない日付など、認識結果が不正な場合。
        return None
    return None


def extract_basic_info(basic_img, iwm=None):
    """中心座標で項目を割り当て、型変換した値（未検出はNone）を返す。"""
    regions = create_regions(basic_img.shape)
    basic_data = extract_basic_data(basic_img, iwm)
    basic_info = dict.fromkeys(regions)
    best_scores = {}

    for data in basic_data:
        center_x, center_y = data["center"]
        key = get_region_key(center_x, center_y, regions)
        if key is None:
            continue
        # 同じ区画に複数の結果がある場合は信頼度の高いものを採用する。
        if key not in best_scores or data["score"] > best_scores[key]:
            basic_info[key] = data["text"]
            best_scores[key] = data["score"]

    basic_info = {key: parse_basic_value(key, text) for key, text in basic_info.items()}
    return basic_info

def main():
    # 画像の選択
    img_path = select_img_path()
    if img_path is None:
        return

    # 画像の読み込み
    img = load_image(img_path)
    if img is None:
        return

    # 画像のトリミング
    img_dict = trimming_image(img)

    # ウィンドウマネージャ
    iwm = IWM()

    basic_info = extract_basic_info(img_dict["basic_img"], iwm)
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
