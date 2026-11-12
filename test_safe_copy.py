import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from safe_copy import copy_files
from preview import plan

class CopyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.src = self.base / 'source'
        self.src.mkdir()
        (self.src / 'a.txt').write_bytes(b'first\x00data')
        (self.src / 'తెలుగు.txt').write_text('తెలుగు', encoding='utf-8')
        (self.src / 'subfolder').mkdir()
        self.before = {p.name: p.read_bytes() for p in self.src.iterdir() if p.is_file()}
    def test_copy_bytes_and_originals(self):
        rows = plan(self.src, 'Product', 10)
        out, count = copy_files(self.src, 'Product', 10, self.base, rows)
        self.assertEqual(count, 2)
        self.assertEqual([p.name for p in sorted(out.iterdir())], ['Product_010.txt','Product_011.txt'])
        for old, new in rows:
            self.assertEqual((out/new).read_bytes(), self.before[old])
        self.assertEqual(self.before, {p.name:p.read_bytes() for p in self.src.iterdir() if p.is_file()})
    def test_repeat_creates_separate_folder(self):
        a, _ = copy_files(self.src, 'Product', 1, self.base)
        (a/'Product_001.txt').write_bytes(b'keep this')
        b, _ = copy_files(self.src, 'Product', 1, self.base)
        self.assertNotEqual(a,b)
        self.assertEqual((a/'Product_001.txt').read_bytes(), b'keep this')
    def test_reject_source_or_child_output(self):
        for parent in [self.src, self.src/'subfolder']:
            with self.assertRaises(ValueError): copy_files(self.src,'Product',1,parent)
    def test_changed_list_requires_preview(self):
        rows = plan(self.src,'Product',1)
        (self.src/'new.txt').write_text('new')
        with self.assertRaises(ValueError): copy_files(self.src,'Product',1,self.base,rows)
    def test_empty_source(self):
        with self.assertRaises(ValueError): copy_files(self.src/'subfolder','Product',1,self.base)
    def test_symlink_excluded(self):
        try: (self.src/'link.txt').symlink_to(self.src/'a.txt')
        except OSError: self.skipTest('Symlinks unavailable')
        out, count = copy_files(self.src,'Product',1,self.base)
        self.assertEqual(count, 2)
    def test_failed_copy_preserves_originals(self):
        with patch('safe_copy.shutil.copyfileobj', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError, 'Partial copies'): copy_files(self.src,'Product',1,self.base)
        self.assertEqual(self.before, {p.name:p.read_bytes() for p in self.src.iterdir() if p.is_file()})

if __name__ == '__main__': unittest.main()
