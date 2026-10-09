import re

from .field_matcher import get_region_key, resolve_regions
from .image_splitter import crop_image
from .value_parser import parse_value


def extract_region(image, section, engine, window_manager=None, window_name="ocr_img"):
    """切り出し済みの画像を、アプリごとの項目定義に従って処理する。"""
    fields = section["fields"]
    if not fields:
        return {}
    regions = resolve_regions(image.shape, fields)
    values = dict.fromkeys(key for key, field in fields.items() if not field.get("ignore", False))
    best_scores = {}
    detections = engine.predict(image, **section.get("ocr_options", {}))
    # 数字を含む結果の選別は、画面を処理する側で行う。
    if section.get("numeric_only", True):
        detections = [detection for detection in detections if re.search(r"\d", detection["text"])]
    for detection in detections:
        center_x, center_y = detection["center"]
        key = get_region_key(center_x, center_y, regions)
        if key is None or fields[key].get("ignore", False):
            continue
        value = parse_value(detection["text"], fields[key])
        if value is not None and (key not in best_scores or detection["score"] > best_scores[key]):
            values[key] = value
            best_scores[key] = detection["score"]
    if window_manager is not None:
        from .utils.image_window_manager import show_detections
        show_detections(image, detections, window_manager, window_name)
    return values


def extract_running_data(image, layout, engine, sections=None, window_manager=None):
    """渡された OCR エンジンを各領域で再利用し、領域ごとの辞書を返す。"""
    names = sections if sections is not None else [name for name, section in layout.items() if section["fields"]]
    return {name: extract_region(crop_image(image, layout[name]["crop"]), layout[name], engine, window_manager,
                                 window_name=f"ocr_{name}")
            for name in names}
