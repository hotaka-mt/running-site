import cv2 as cv

class ImageWindowManager:
    def __init__(self):
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