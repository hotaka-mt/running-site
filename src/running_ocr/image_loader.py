import os
import cv2 as cv

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

