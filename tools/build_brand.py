from pathlib import Path
from PIL import Image,ImageDraw
out=Path("assets");out.mkdir(exist_ok=True)
im=Image.new("RGBA",(768,768));d=ImageDraw.Draw(im)
def b(c):return tuple(v*3 for v in c)
for c,r,col in [((12,12,244,244),52,"#33372d"),((57,37,212,221),20,"#ae9b49"),((65,43,204,209),15,"#e9cf71")]:d.rounded_rectangle(b(c),r*3,fill=col)
d.line(b((86,44,86,209)),fill="#8b793b",width=18)
for x,y in [(177,89),(164,112),(177,135)]:d.rounded_rectangle(b((109,y-4,x,y+4)),12,fill="#59563d")
d.line(b((161,176,181,154)),fill="#f9f5e8",width=27)
d.ellipse(b((179,173,191,185)),fill="#777d49")
for y in (80,125,170):d.rounded_rectangle(b((48,y-4,77,y+4)),12,fill="#f4e6a5")
im=im.resize((256,256),Image.Resampling.LANCZOS)
im.save(out/"lumen.ico",sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
banner=Image.new("RGB",(164,314));draw=ImageDraw.Draw(banner)
for y in range(314):
    t=y/313;draw.line((0,y,164,y),fill=(int(45+40*t),int(50+34*t),int(36+11*t)))
draw.ellipse((-95,185,180,440),fill="#a08e4f")
logo=im.resize((120,120));banner.paste(logo,(22,76),logo);banner.save(out/"wizard.bmp")
small=Image.new("RGB",(55,55),"#f9f7ed");logo=im.resize((49,49));small.paste(logo,(3,3),logo);small.save(out/"wizard-small.bmp")
