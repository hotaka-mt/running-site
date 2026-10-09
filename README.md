# running-site

ランニングの記録画像からデータを抽出し、Web ページで表示するためのプロジェクト。

## 開発環境

- Python 3.13 以上
- uv
- OpenCV
- Ubuntu / GNOME（Wayland）

## 今後やること

- 画像からランニングデータを抽出する
- 抽出したデータを保存する
- Web ページに記録を表示する

## OCR の実行

```sh
uv sync
uv run python main.py
```

`img/` の JPG を選択すると、Mi Fitness の基本情報8項目を表示します。
GUI の OCR 確認ウィンドウは `q` で閉じます。従来の
`uv run python extraction_running_data.py` も利用できます。

`src/running_ocr/` は画像の読み込み・切り出し、OCR、区画判定、型変換、
パイプラインに責務を分けています。画面の座標・パーサー・単位・タイムゾーンは
`layouts/mi_fitness.py` に定義します。区画は半開区間で、`None` は画像の端です。
項目を定義した領域では、画像全体を重複や隙間なく覆う必要があります。
切り出し座標は既存のスクリーンショットの固定レイアウトを前提とします。

```python
from running_ocr.image_loader import load_image
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT
from running_ocr.ocr_engine import OCREngine
from running_ocr.pipeline import extract_running_data

engine = OCREngine()  # 複数の画像・領域で同じモデルを再利用
image = load_image("img/2026-10-05.jpg")
data = extract_running_data(image, MI_FITNESS_LAYOUT, engine)
```

戻り値は領域名ごとの辞書です。未検出の項目は `None`、日時はタイムゾーン付き
`datetime`、時間とペースは秒、距離は km、その他の基本項目は整数です。
同じ区画の候補が複数ある場合、型変換に成功した中で信頼度が最も高い値を採用します。
心拍数など、`fields` が空の領域は既定の処理対象から外れます。
他アプリも同じ構造のレイアウトを渡すことで処理できます。

## テスト

```sh
uv run python -m unittest discover -s tests -v
```

モデルを起動せず、基本情報8項目、区画の境界・重複・隙間、不正値、
候補の信頼度選択、モデルの再利用、別レイアウトを検証します。
