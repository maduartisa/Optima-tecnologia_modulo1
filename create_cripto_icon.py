from pathlib import Path
from PIL import Image, ImageDraw

base = Path(__file__).resolve().parent
ico_path = base / 'criptor_lock.ico'
size = (256, 256)
img = Image.new('RGBA', size, (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# lock body
body = [(64, 120), (192, 220)]
d.rectangle(body, fill=(70, 130, 180, 255), outline=(10, 10, 10, 255), width=10)

# lock shackle
shackle_box = [(64, 36), (192, 180)]
d.arc(shackle_box, start=0, end=180, fill=(200, 200, 200, 255), width=24)
d.line([(64, 108), (64, 132)], fill=(200, 200, 200, 255), width=24)
d.line([(192, 108), (192, 132)], fill=(200, 200, 200, 255), width=24)

# keyhole
hole_top = [(118, 150), (138, 170)]
d.ellipse(hole_top, fill=(0, 0, 0, 255))
d.rectangle([(128, 170), (132, 190)], fill=(0, 0, 0, 255))

# shine highlight
for i in range(5):
    d.line([(84 + i * 6, 140 - i * 6), (98 + i * 6, 126 - i * 6)], fill=(255, 255, 255, 200), width=2)

img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32)])
print('ICON_CREATED', ico_path)
