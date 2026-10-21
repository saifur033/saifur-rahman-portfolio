import os, tempfile, unittest
from io import BytesIO
from PIL import Image
from portfolio import create_app
from portfolio.utils import save_upload
class SaveUploadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); base=self.tmp.name
  self.media=os.path.join(base,'media'); os.makedirs(self.media)
  self.app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'DATABASE':os.path.join(base,'t.sqlite3'),'MEDIA_DIR':self.media,'SECRET_KEY':'test-only-secret'})
 def tearDown(self): self.tmp.cleanup()
 def _file(self, data, name):
  from werkzeug.datastructures import FileStorage
  return FileStorage(stream=BytesIO(data), filename=name)
 def test_oversized_file_rejected(self):
  with self.app.app_context():
   class Big:
    filename='big.png'
    stream=BytesIO(b'x'*(8*1024*1024+2))
   with self.assertRaises(ValueError):
    save_upload(Big())
 def test_empty_file_rejected(self):
  with self.app.app_context():
   with self.assertRaises(ValueError):
    save_upload(self._file(b'', 'empty.png'))
 def test_blocked_extension_rejected(self):
  with self.app.app_context():
   for name in ('evil.exe','script.sh','page.html','run.php'):
    with self.assertRaises(ValueError):
     save_upload(self._file(b'MZ\x90\x00', name))
 def test_non_image_non_pdf_rejected(self):
  with self.app.app_context():
   with self.assertRaises(ValueError):
    save_upload(self._file(b'this is just text, not an image', 'notes.txt'))
 def test_valid_pdf_passthrough(self):
  with self.app.app_context():
   pdf=b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
   result=save_upload(self._file(pdf,'cv.pdf'), allow_pdf=True)
   self.assertEqual(result['mime'],'application/pdf')
   self.assertTrue(result['filename'].endswith('.pdf'))
   self.assertTrue(os.path.exists(os.path.join(self.media,result['filename'])))
   self.assertEqual(open(os.path.join(self.media,result['filename']),'rb').read(),pdf)
 def test_valid_pdf_rejected_without_allow_pdf(self):
  with self.app.app_context():
   pdf=b'%PDF-1.4\n%%EOF'
   with self.assertRaises(ValueError):
    save_upload(self._file(pdf,'cv.pdf'))
 def test_valid_image_saved_as_webp(self):
  buf=BytesIO(); Image.new('RGB',(2,2),'red').save(buf,format='PNG'); buf.seek(0)
  with self.app.app_context():
   result=save_upload(self._file(buf.getvalue(),'photo.png'))
   self.assertEqual(result['mime'],'image/webp')
   self.assertTrue(os.path.exists(os.path.join(self.media,result['filename'])))
if __name__=='__main__': unittest.main()
