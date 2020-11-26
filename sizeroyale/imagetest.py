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


img_url = "https://moonvillageassociation.org/wp-content/uploads/2018/06/default-profile-picture1.jpg"
size = (200, 200)

r = requests.get(img_url, stream=True)
if r.status_code == 200:
    i = Image.open(io.BytesIO(r.content))
else:
    raise Exception("You idiot. You absolute fool.")

i = crop_max_square(i)
i.show(title = "Wow.")
