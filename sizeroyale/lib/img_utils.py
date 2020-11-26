from PIL import Image, ImageDraw
from PIL.ImageOps import grayscale


# https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
def crop_center(pil_img: Image, crop_width, crop_height) -> Image:
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


# https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
def crop_max_square(pil_img: Image) -> Image:
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def merge_images(images: list) -> Image:
    widths = [i.size[0] for i in images]
    heights = [i.size[1] for i in images]

    result_width = sum(widths)
    result_height = max(heights)

    result = Image.new('RGB', (result_width, result_height))

    current_width = 0
    for i in images:
        result.paste(im=i, box=(current_width, 0))
        current_width += i.size[0]
    return result


def kill(image: Image, *, gray: bool = True, x: bool = True, color = (255, 0, 0), width: int = 5) -> Image:
    i = image
    if gray:
        i = grayscale(i)
        rgbimg = Image.new("RGBA", i.size)
        rgbimg.paste(i)
        i = rgbimg
    if x:
        draw = ImageDraw.Draw(i)
        draw.line((0, 0) + i.size, fill = color, width = width)
        draw.line((0, i.size[1], i.size[0], 0), fill = color, width = width)
    return i
