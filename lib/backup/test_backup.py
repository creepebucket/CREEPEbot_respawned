import tempfile
import unittest
from pathlib import Path

import lib.backup as backup


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, key, direction):
        self.docs.sort(key=lambda d: d[key], reverse=direction < 0)
        return self

    def __iter__(self):
        return iter(self.docs)


class FakeCollection:
    def __init__(self):
        self.docs = []

    def find_one(self, filt, sort=None):
        docs = [d for d in self.docs if all(d.get(k) == v for k, v in filt.items())]
        if not docs:
            return None
        if sort:
            key, direction = sort[0]
            docs.sort(key=lambda d: d[key], reverse=direction < 0)
        return docs[0]

    def insert_one(self, doc):
        self.docs.append(doc)

    def find(self, filt, proj=None):
        docs = []
        for d in self.docs:
            if not all(d.get(k) == v for k, v in filt.items()):
                continue
            doc = dict(d)
            if proj:
                for k, v in proj.items():
                    if v == 0 and k in doc:
                        del doc[k]
            docs.append(doc)
        return _Cursor(docs)


class BackupTests(unittest.TestCase):
    def setUp(self):
        backup.backup_collection = FakeCollection()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_text_files(self, mapping):
        for rel_path, text in mapping.items():
            path = self.root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')

    def test_backup_incremental_and_restore(self):
        (self.root / 'a.txt').write_text('one', encoding='utf-8')
        (self.root / 'sub').mkdir()
        (self.root / 'sub' / 'b.txt').write_text('two', encoding='utf-8')

        first = backup.start_backup(str(self.root), 'first')
        self.assertEqual(first['file_count'], 2)
        self.assertEqual(first['changed_files'], 2)
        self.assertEqual(first['reused_files'], 0)

        (self.root / 'a.txt').write_text('ONE', encoding='utf-8')
        (self.root / 'c.txt').write_text('three', encoding='utf-8')

        second = backup.start_backup(str(self.root), 'second')
        self.assertEqual(second['file_count'], 3)
        self.assertEqual(second['reused_files'], 1)
        self.assertEqual(second['changed_files'], 2)

        backups = backup.list_backup(str(self.root))
        self.assertEqual(backups[0]['name'], 'second')
        self.assertEqual(backups[1]['name'], 'first')
        self.assertNotIn('manifest_path', backups[0])

        backup.restore_backup(str(self.root), first['time'])
        self.assertEqual((self.root / 'a.txt').read_text(encoding='utf-8'), 'one')
        self.assertEqual((self.root / 'sub' / 'b.txt').read_text(encoding='utf-8'), 'two')
        self.assertFalse((self.root / 'c.txt').exists())

        backup_root = self.root / backup.BACKUP_DIRNAME
        self.assertTrue((backup_root / backup.BLOB_DIRNAME).exists())
        self.assertTrue((backup_root / backup.MANIFEST_DIRNAME).exists())

    def test_restore_more_than_10_small_files(self):
        files = {f'small/{i}.txt': f'v{i}' for i in range(12)}
        self._write_text_files(files)
        first = backup.start_backup(str(self.root), 'many_small')

        changed = dict(files)
        changed['small/3.txt'] = 'changed'
        changed['small/11.txt'] = 'changed2'
        changed['small/new.txt'] = 'new'
        self._write_text_files(changed)
        second = backup.start_backup(str(self.root), 'many_small_v2')

        backup.restore_backup(str(self.root), first['time'])
        for rel_path, text in files.items():
            self.assertEqual((self.root / rel_path).read_text(encoding='utf-8'), text)
        self.assertFalse((self.root / 'small/new.txt').exists())

        backup.restore_backup(str(self.root), second['time'])
        self.assertEqual((self.root / 'small/3.txt').read_text(encoding='utf-8'), 'changed')
        self.assertEqual((self.root / 'small/11.txt').read_text(encoding='utf-8'), 'changed2')
        self.assertEqual((self.root / 'small/new.txt').read_text(encoding='utf-8'), 'new')

    def test_restore_large_file(self):
        data = (b'0123456789abcdef' * 1024 * 256)
        (self.root / 'big.bin').write_bytes(data)
        first = backup.start_backup(str(self.root), 'big_v1')

        data2 = (b'fedcba9876543210' * 1024 * 256)
        (self.root / 'big.bin').write_bytes(data2)
        second = backup.start_backup(str(self.root), 'big_v2')

        backup.restore_backup(str(self.root), first['time'])
        self.assertEqual((self.root / 'big.bin').read_bytes(), data)

        backup.restore_backup(str(self.root), second['time'])
        self.assertEqual((self.root / 'big.bin').read_bytes(), data2)

    def test_restore_one_backup_then_backward_then_forward(self):
        self._write_text_files({'a.txt': '1'})
        only = backup.start_backup(str(self.root), 'only')
        backup.restore_backup(str(self.root), only['time'])
        self.assertEqual((self.root / 'a.txt').read_text(encoding='utf-8'), '1')

        self._write_text_files({'a.txt': '2', 'b.txt': 'x'})
        second = backup.start_backup(str(self.root), 'second')
        self._write_text_files({'a.txt': '3', 'b.txt': 'y', 'c.txt': 'z'})
        third = backup.start_backup(str(self.root), 'third')

        backup.restore_backup(str(self.root), second['time'])
        self.assertEqual((self.root / 'a.txt').read_text(encoding='utf-8'), '2')
        self.assertEqual((self.root / 'b.txt').read_text(encoding='utf-8'), 'x')
        self.assertFalse((self.root / 'c.txt').exists())

        backup.restore_backup(str(self.root), third['time'])
        self.assertEqual((self.root / 'a.txt').read_text(encoding='utf-8'), '3')
        self.assertEqual((self.root / 'b.txt').read_text(encoding='utf-8'), 'y')
        self.assertEqual((self.root / 'c.txt').read_text(encoding='utf-8'), 'z')


if __name__ == '__main__':
    unittest.main()
