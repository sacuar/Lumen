"""Read-only local document preview providers."""
from pathlib import Path
import base64,io
IMAGES={".png",".jpg",".jpeg",".bmp",".gif",".webp",".tif",".tiff",".ico"}
TYPES=IMAGES|{".pdf",".docx"}
def supports(path):return Path(path).suffix.lower() in TYPES
def png(img):
    img.thumbnail((1200,1500));buf=io.BytesIO();img.convert("RGBA").save(buf,format="PNG")
    return "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode("ascii")
def render(path,page=0):
    p=Path(path);ext=p.suffix.lower()
    if not p.is_file() or not supports(p):raise ValueError("Unsupported preview")
    if p.stat().st_size>32*1024*1024:raise ValueError("Preview limit: 32 MB")
    out={"name":p.name,"page":0,"pages":1}
    if ext in IMAGES:
        from PIL import Image,ImageOps
        with Image.open(p) as im:
            if im.width*im.height>40000000:raise ValueError("Image too large")
            out.update(kind="image",data=png(ImageOps.exif_transpose(im)))
    elif ext==".pdf":
        import pypdfium2 as pdfium
        doc=pdfium.PdfDocument(str(p))
        try:
            n=len(doc)
            if not n:raise ValueError("Empty PDF")
            i=max(0,min(int(page),n-1));pg=doc[i]
            try:
                w,h=pg.get_size();bm=pg.render(scale=min(2,1200/max(w,1),1500/max(h,1)))
                try:out.update(kind="image",data=png(bm.to_pil()),page=i,pages=n)
                finally:bm.close()
            finally:pg.close()
        finally:doc.close()
    else:
        from zipfile import ZipFile
        with ZipFile(p) as z:
            if sum(x.file_size for x in z.infolist())>64*1024*1024:raise ValueError("Expanded document too large")
        from docx import Document
        doc=Document(str(p));lines=[x.text for x in doc.paragraphs]
        for t in doc.tables:lines.extend(" | ".join(c.text for c in row.cells) for row in t.rows)
        out.update(kind="text",data="\n".join(lines)[:200000])
    return out
