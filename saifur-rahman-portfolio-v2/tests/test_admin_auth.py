import unittest
from portfolio import create_app
from portfolio import admin as admin_module
class AdminAuthTests(unittest.TestCase):
 def setUp(self):
  admin_module.ATTEMPTS.clear()
  import os, tempfile
  self.tmp=tempfile.TemporaryDirectory(); base=self.tmp.name
  self.db=os.path.join(base,'test.sqlite3'); self.media=os.path.join(base,'media'); os.makedirs(self.media)
  self.app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'DATABASE':self.db,'MEDIA_DIR':self.media,'SECRET_KEY':'test-only-secret'})
  self.client=self.app.test_client()
 def tearDown(self): self.tmp.cleanup()
 def _setup(self, email='admin@example.com', password='very-long-test-password'):
  return self.client.post('/studio/setup',data={'email':email,'password':password,'confirm':password})
 def test_setup_rejects_invalid_email(self):
  r=self.client.post('/studio/setup',data={'email':'not-an-email','password':'very-long-test-password','confirm':'very-long-test-password'})
  self.assertEqual(r.status_code,200); self.assertIn(b'valid email',r.data)
  with self.app.app_context():
   from portfolio.db import get_db
   self.assertEqual(get_db().execute('SELECT COUNT(*) FROM admins').fetchone()[0],0)
 def test_setup_rejects_short_or_mismatched_password(self):
  r=self.client.post('/studio/setup',data={'email':'a@example.com','password':'short','confirm':'short'})
  self.assertIn(b'at least 12',r.data)
  r=self.client.post('/studio/setup',data={'email':'a@example.com','password':'very-long-test-password','confirm':'different-password'})
  self.assertIn(b'matching password',r.data)
 def test_setup_redirects_to_login_once_admin_exists(self):
  self._setup(); self.client.post('/studio/logout')
  with self.client.session_transaction() as sess: sess.clear()
  r=self.client.get('/studio/setup')
  self.assertEqual(r.status_code,302)
  r=self.client.post('/studio/setup',data={'email':'x@example.com','password':'another-long-password','confirm':'another-long-password'})
  self.assertEqual(r.status_code,302)
 def test_login_throttles_after_five_failures(self):
  self._setup()
  with self.client.session_transaction() as sess: sess.clear()
  for i in range(5):
   r=self.client.post('/studio/login',data={'email':'admin@example.com','password':'wrong-password'})
   self.assertIn(b'Email or password is incorrect',r.data)
  r=self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  self.assertIn(b'Too many login attempts',r.data)
  with self.client.session_transaction() as sess: self.assertFalse(sess.get('admin_id'))
 def test_successful_login_sets_session_state(self):
  self._setup()
  self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  with self.client.session_transaction() as sess:
   self.assertTrue(sess.get('admin_id'))
   self.assertEqual(sess.get('admin_email'),'admin@example.com')
  self.assertEqual(self.client.get('/studio/dashboard').status_code,200)
 def test_admin_required_redirects_anonymous(self):
  self.assertEqual(self.client.get('/studio/dashboard').status_code,302)
  self.assertIn('/studio/login',self.client.get('/studio/dashboard').headers['Location'])
  self.assertEqual(self.client.get('/studio/profile').status_code,302)
  self.assertEqual(self.client.get('/studio/project').status_code,302)
 def test_logout_clears_session(self):
  self._setup(); self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  self.client.post('/studio/logout')
  with self.client.session_transaction() as sess:
   self.assertFalse(sess.get('admin_id'))
  self.assertEqual(self.client.get('/studio/dashboard').status_code,302)
if __name__=='__main__': unittest.main()
