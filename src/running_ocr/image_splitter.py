def crop_image(image, crop):
    """半開区間で指定した行を画像の全幅で切り出す。None は画像の端を表す。"""
    start, end = crop
    start = 0 if start is None else start
    end = image.shape[0] if end is None else end
    if not 0 <= start < end <= image.shape[0]:
        raise ValueError(f"Invalid crop {crop} for image height {image.shape[0]}")
    return image[start:end, :]


def split_image(image, layout):
    return {name: crop_image(image, section["crop"]) for name, section in layout.items()}
