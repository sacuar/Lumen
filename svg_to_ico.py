# svg_to_ico.py  (run once)
import cairosvg
from PIL import Image
import io, os

SIZES = [16, 24, 32, 48, 64, 128, 256]

png = cairosvg.svg2png(url="lumen.svg", output_width=256, output_height=256)
img = Image.open(io.BytesIO(png)).convert("RGBA")

frames = [img.resize((s, s), Image.LANCZOS) for s in SIZES]
frames[0].save(
    "lumen.ico",
    format="ICO",
    sizes=[(s, s) for s in SIZES],
    append_images=frames[1:],
)
print("wrote lumen.ico", os.path.getsize("lumen.ico"), "bytes")