import os
import cv2 as cv

# 環境変数の設定（cv.imshowを使うために必要）
os.environ.pop("XDG_SESSION_TYPE", None)
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts/truetype/dejavu"


def select_img_path(directory_path="img/"):
    # 読み込む画像パスを選択する
    # 引数はディレクトリパス、デフォルトはリポジトリ内のimgフォルダ

    # ディレクトリ内のjpgファイルを取得
    img_files = [f for f in os.listdir(directory_path) if f.endswith((".jpg"))]

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
        if selected_index < 0 or selected_index >= len(img_files):
            print("存在しない番号です。もう一度入力してください。")
            for index, img_file in enumerate(img_files):
                print(f"画像{index+1}: {img_file}")
        else:
            break

    # 選択された画像のパスを返す
    return os.path.join(directory_path, img_files[selected_index])


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

def extract_basic_info(basic_img):
    basic_gray = cv.cvtColor(basic_img, cv.COLOR_BGR2GRAY)
    cv.imshow("basic_gray", basic_gray)

    # 2値化処理
    _, basic_binary = cv.threshold(basic_gray, 50, 255, cv.THRESH_BINARY)

    cv.imshow("basic_binary", basic_binary)

def main():
    img_path = select_img_path()

    img = load_image(img_path)
    if img is None:
        return

    # cv.namedWindow("選択画像", cv.WINDOW_NORMAL)
    # cv.resizeWindow("選択画像", 402, 4070)
    # cv.imshow("選択画像", img)

    img_dict = trimming_image(img)

    while True:
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        extract_basic_info(img_dict["basic_img"])

        # cv.imshow("ランニングコース", img_dict["map_img"])
        # cv.imshow("ランニング基本情報", img_dict["basic_img"])
        # cv.imshow("ランニング心拍数情報", img_dict["bpm_img"])
        # cv.imshow("ランニングペース情報", img_dict["pace_img"])
        # cv.imshow("ランニングケイデンス情報", img_dict["cadence_img"])
        # cv.imshow("ランニングストライド情報", img_dict["stride_img"])
        # cv.imshow("ランニング効果情報", img_dict["effect_img"])
        # cv.imshow("ランニング強度情報", img_dict["intensity_img"])

    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
