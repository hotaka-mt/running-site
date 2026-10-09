import re


class OCREngine:
    """PaddleOCR のモデルを保持し、数字を含む認識結果を共通形式に整える。"""

    def __init__(self, backend=None):
        if backend is None:
            from paddleocr import PaddleOCR
            backend = PaddleOCR(lang="japan", use_textline_orientation=True)
        self.ocr = backend

    def predict(self, image):
        detections = []
        for result in self.ocr.predict(image):
            for text, score, box in zip(result["rec_texts"], result["rec_scores"], result["rec_boxes"]):
                text = text.strip()
                # 数字を含まない文字ラベルは、後続の処理や描画の対象から除外する。
                if re.search(r"\d", text) is None:
                    continue
                x1, y1, x2, y2 = map(int, box)
                detections.append({"text": text, "score": float(score),
                                   "box": (x1, y1, x2, y2),
                                   "center": ((x1 + x2) // 2, (y1 + y2) // 2)})
        return detections
