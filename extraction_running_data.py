import os
import cv2 as cv
from image_window_manager import ImageWindowManager as IWM

# 環境変数の設定（cv.imshowを使うために必要）
os.environ.pop("XDG_SESSION_TYPE", None)
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts/truetype/dejavu"


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

def extract_basic_info(basic_img, iwm=None):
    # グレースケール変換
    basic_gray = cv.cvtColor(basic_img, cv.COLOR_BGR2GRAY)

    # 2値化処理
    _, basic_binary = cv.threshold(basic_gray, 50, 255, cv.THRESH_BINARY)

    if iwm:
        iwm.show_image("basic_gray", basic_gray)
        iwm.show_image("basic_binary", basic_binary)

    return basic_binary

def main():
    img_path = select_img_path()
    if img_path is None:
        return

    img = load_image(img_path)
    if img is None:
        return

    # ウィンドウマネージャ
    iwm = IWM()

    # cv.namedWindow("選択画像", cv.WINDOW_NORMAL)
    # cv.resizeWindow("選択画像", 402, 4070)
    # cv.imshow("選択画像", img)

    img_dict = trimming_image(img)
    extract_basic_info(img_dict["basic_img"], iwm)

    iwm.wait()


if __name__ == "__main__":
    main()
