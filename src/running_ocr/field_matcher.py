def resolve_regions(image_shape, fields):
    """画像の端を座標に置き換え、区画が重複や隙間なく画像全体を覆うことを検証する。"""
    height, width = image_shape[:2]
    regions = {}
    for key, field in fields.items():
        x1, y1, x2, y2 = field["region"]
        region = (0 if x1 is None else x1, 0 if y1 is None else y1,
                  width if x2 is None else x2, height if y2 is None else y2)
        x1, y1, x2, y2 = region
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError(f"Invalid region for {key}: {region}")
        for other in regions.values():
            if max(x1, other[0]) < min(x2, other[2]) and max(y1, other[1]) < min(y2, other[3]):
                raise ValueError(f"Overlapping region: {key}")
        regions[key] = region
    if sum((r[2] - r[0]) * (r[3] - r[1]) for r in regions.values()) != width * height:
        raise ValueError("Regions must cover the entire image without gaps")
    return regions


def get_region_key(center_x, center_y, regions):
    for key, (x1, y1, x2, y2) in regions.items():
        if x1 <= center_x < x2 and y1 <= center_y < y2:
            return key
    return None


