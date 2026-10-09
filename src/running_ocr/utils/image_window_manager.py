import cv2 as cv
import os


class ImageWindowManager:
    def __init__(self):
        # ウィンドウマネージャが生成されたときに GUI の環境を設定する。
        os.environ.pop("XDG_SESSION_TYPE", None)
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts/truetype/dejavu"
        self.open_windows = set()

    def show_image(self, window_name, image):
        cv.imshow(window_name, image)
        self.open_windows.add(window_name)

    def has_open_window(self):
        for name in self.open_windows:
            try:
                if cv.getWindowProperty(name, cv.WND_PROP_VISIBLE) > 0:
                    return True
            except cv.error:
                continue
        return False

    def wait(self, key="q", timeout=30):
        while True:
            if not self.has_open_window():
                break
            k = cv.waitKey(timeout) & 0xFF
            if k == ord(key):
                break
        self.close()

    def close(self):
        for name in self.open_windows:
            try: 
                if cv.getWindowProperty(name, cv.WND_PROP_VISIBLE) > 0:
                    cv.destroyWindow(name)
            except cv.error:
                continue
        self.open_windows.clear()


def show_detections(image, detections, manager, window_name="ocr_img"):
    annotated = image.copy()
    for detection in detections:
        x1, y1, x2, y2 = detection["box"]
        cv.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv.putText(annotated, f"{detection['text']} ({detection['score']:.2f})", (x1, y1),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    manager.show_image(window_name, annotated)
