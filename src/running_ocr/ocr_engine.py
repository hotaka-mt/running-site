class OCREngine:
    """PaddleOCR のモデルを保持し、すべての認識結果を共通形式に整える。"""

    def __init__(self, backend=None):
        if backend is None:
            from paddleocr import PaddleOCR
            # スクリーンショットの上下は保証されるため、向きの自動補正は行わない。
            backend = PaddleOCR(
                lang="japan",
                use_doc_orientation_classify=False,
                use_textline_orientation=False,
            )
        self.ocr = backend

    def predict(self, image, **options):
        detections = []
        for result in self.ocr.predict(image, **options):
            for text, score, box in zip(result["rec_texts"], result["rec_scores"], result["rec_boxes"]):
                text = text.strip()
                x1, y1, x2, y2 = map(int, box)
                detections.append({"text": text, "score": float(score),
                                   "box": (x1, y1, x2, y2),
                                   "center": ((x1 + x2) // 2, (y1 + y2) // 2)})
        return detections
