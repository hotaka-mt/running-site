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

`img/` の JPG を選択すると、Mi Fitness の map 以外の7領域・30項目を単位付きで表示します。
GUI の OCR 確認ウィンドウは `ocr_basic`・`ocr_bpm` など領域ごとに分かれ、`q` で閉じます。

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
map のように、`fields` が空の領域は既定の処理対象から外れます。
他アプリも同じ構造のレイアウトを渡すことで処理できます。

`extract_running_data()` は既定で map 以外の7領域・30項目を処理します。
`main.py` も同じ7領域を処理し、領域ごとに結果を端末へ表示します。

| 領域 | 抽出する項目 | 値の単位・型 |
| --- | --- | --- |
| pace | 平均・最高ペース、kmごとのペース3行 | 秒/km |
| cadence | 平均・最高ケイデンス | 整数（回/分） |
| stride | 平均・最大ストライド | 整数（cm） |
| effect | 有酸素・無酸素効果、最大酸素摂取量、負荷、回復時間 | 効果は小数、酸素摂取量は ml/kg/min、負荷は TL、回復は時間 |
| intensity | トレーニングの強度 | 文字列（例：普通） |

ペースの引用符の誤認識は項目定義の置換ルールで補正します。
現在の km ごとのペースは、保存済み画像に合わせた3行の固定区画です。
最終行は1 km未満の区間も含みます。行数や画面の高さが変わる場合は、
行の区画と後続領域の切り出し座標も調整する必要があります。

OCR Engine は文字ラベルを含む全検出結果を返します。Pipeline では既定で数字を
含む結果だけを抽出・描画します。領域に `numeric_only: False` を指定すると、
文字ラベルも後続処理へ渡せます。

心拍数領域は平均・最大心拍数と5種類のゾーン滞在時間（秒）を読み取ります。
グラフの区画は `ignore: True` として結果の辞書から除外し、区画の完全性は検証します。
グラフの線から時系列の心拍数を取得する処理は含みません。
画像の上下は保証されるため、OCR Engine では画像・文字行の向き補正を無効にしています。
心拍数領域の歪み補正の無効化と、最大酸素摂取量の行の時刻区切りを `.` から `:` に
置換する設定は、レイアウト定義で指定しています。

## テスト

```sh
uv run python -m unittest discover -s tests -v
```

モデルを起動せず、map 以外の全30項目、区画の境界・重複・隙間、不正値、
候補の信頼度選択、モデルの再利用、別レイアウト、領域別ウィンドウを検証します。
`tests/fixtures/mi_fitness_ocr.json` は保存済み画像3枚から取得した OCR 結果と
目視確認済みの期待値です。画像やモデルがなくても、同じ結果を再生して回帰確認できます。
