import tempfile
import unittest
from pathlib import Path
from preview import plan

class PreviewTests(unittest.TestCase):
    def test_preview_preserves_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'తెలుగు.txt').write_text('sample',encoding='utf-8')
            (p/'photo.jpg').write_bytes(b'demo')
            (p/'subfolder').mkdir()
            before={x.name:x.read_bytes() for x in p.iterdir() if x.is_file()}
            rows=plan(p,'Product',1)
            self.assertEqual(rows,[('photo.jpg','Product_001.jpg'),('తెలుగు.txt','Product_002.txt')])
            self.assertEqual(before,{x.name:x.read_bytes() for x in p.iterdir() if x.is_file()})
    def test_invalid_prefix(self):
        with tempfile.TemporaryDirectory() as d:
            for prefix in ('','../escape','a/b','a\\b','bad?name'):
                with self.assertRaises(ValueError): plan(d,prefix,1)
    def test_empty_and_start(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(plan(d,'Product',0),[])
            with self.assertRaises(ValueError): plan(d,'Product',-1)

if __name__=='__main__': unittest.main()
