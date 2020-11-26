import io

from PIL import Image
import requests


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

imgs = []

size = (200, 200)

for img_url in img_urls:
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        i = Image.open(io.BytesIO(r.content))
    else:
        raise Exception("You idiot. You absolute fool.")

    i = crop_max_square(i)
    i = i.resize(size)
    imgs.append(i)

print(imgs)
merge_images(imgs).show()
