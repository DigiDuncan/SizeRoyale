import io
import os

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageOps import grayscale
import requests


def truncate(s, amount) -> str:
    """Return a string that is no longer than the amount specified."""
    if len(s) > amount:
        return s[:amount - 3] + "..."
    return s


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def merge_images(images):

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


img_urls = ["https://moonvillageassociation.org/wp-content/uploads/2018/06/default-profile-picture1.jpg",
            "https://randomuser.me/api/portraits/men/90.jpg",
            "https://randomuser.me/api/portraits/women/50.jpg",
            "https://randomuser.me/api/portraits/lego/1.jpg",
            "https://randomuser.me/api/portraits/men/30.jpg",
            "https://randomuser.me/api/portraits/women/17.jpg"]

alives = [True, False, True, True, False, True]
names = ["Ya Boi", "Man Oh Man I'm A Man My Man", "Alex", "Robin", "Zxyqu", "This Is Not A Name"]

imgs = []

size = (200, 200)

for n, img_url in enumerate(img_urls):
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        i = Image.open(io.BytesIO(r.content))
    else:
        raise Exception("You idiot. You absolute fool.")

    i = crop_max_square(i)
    i = i.resize(size)
    rgbimg = Image.new("RGBA", i.size)
    rgbimg.paste(i)
    i = rgbimg
    d = ImageDraw.Draw(i)
    fnt = ImageFont.truetype(os.environ['WINDIR'] + "\\Fonts\\arial.ttf", size = 20)
    name = names[n]
    while fnt.getsize(name)[0] > i.width:
        name = truncate(name, len(name) - 1)
    textwidth, textheight = fnt.getsize(name)
    d.text(((i.width - textwidth) // 2, i.height - textheight - 10), name, align = "center", font = fnt, fill = (0, 0, 0), stroke_width = 2, stroke_fill = (255, 255, 255))
    if alives[n] is False:
        i = grayscale(i)
        rgbimg = Image.new("RGBA", i.size)
        rgbimg.paste(i)
        i = rgbimg
        draw = ImageDraw.Draw(i)
        draw.line((0, 0) + i.size, fill = (255, 0, 0), width = 5)
        draw.line((0, i.size[1], i.size[0], 0), fill = (255, 0, 0), width = 5)
    imgs.append(i)

print(imgs)
merge_images(imgs).show()
