import tempfile,unittest
from pathlib import Path
from lumen import preview
class PreviewTests(unittest.TestCase):
    def test_classification(self):
        for path in ("x.PDF","x.png","x.docx"):self.assertTrue(preview.supports(path))
        self.assertFalse(preview.supports("x.py"))
    def test_png(self):
        try:from PIL import Image
        except ImportError:self.skipTest("Pillow not installed")
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"sample.png";Image.new("RGB",(20,20),"white").save(p)
            self.assertTrue(preview.render(p)["data"].startswith("data:image/png;base64,"))
