import json, os, tempfile, unittest
from io import BytesIO
from PIL import Image
from werkzeug.security import check_password_hash
from portfolio import create_app
from portfolio import admin as admin_module
class PortfolioTests(unittest.TestCase):
 def setUp(self):
  admin_module.ATTEMPTS.clear()
  self.tmp=tempfile.TemporaryDirectory(); base=self.tmp.name
  self.db=os.path.join(base,'test.sqlite3'); self.media=os.path.join(base,'media');os.makedirs(self.media)
  self.app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'DATABASE':self.db,'MEDIA_DIR':self.media,'SECRET_KEY':'test-only-secret'})
  self.client=self.app.test_client()
 def tearDown(self): self.tmp.cleanup()
 def test_public_routes_and_health(self):
  self.assertEqual(self.client.get('/').status_code,200);self.assertEqual(self.client.get('/health').json['status'],'ok');self.assertEqual(self.client.get('/studio').status_code,302)
  with self.client.get('/static/css/style.css') as response: self.assertEqual(response.status_code,200)
 def test_portfolio_rooms_and_quick_view_are_rendered(self):
  html=self.client.get('/').data.decode()
  for section in ('about','projects','publications','outreach','certificates','trophies','gallery','contact'):
   self.assertIn(f'id="{section}"',html);self.assertIn(f'data-room="{section}"',html)
  self.assertIn('Projects &amp; Innovation',html);self.assertIn('aria-controls="quickPanel"',html)
  self.assertNotIn('Communication & Outreach Executive',html)
  self.assertNotIn('saifur3734@gmail.com',html)
 def test_published_sections_render_data_driven_experiences(self):
  with self.app.app_context():
   from portfolio.db import get_db
   db=get_db()
   club_id=db.execute("INSERT INTO content(kind,title,slug,data,status) VALUES(?,?,?,?,?)",('club','Research Society','research-society',json.dumps({'relationship':'Member'}),'published')).lastrowid
   records=[
    ('category','Research','research',{}),
    ('career','Research Assistant','research-assistant',{'period':'2024','organization':'Research Society','description':'Published role details.','type':'Role'}),
    ('project','Research Portal','research-portal',{'category':'Research','summary':'Published project summary.','technologies':'Flask, SQLite','featured':'true','objective':'Organize research.'}),
    ('publication','A Published Paper','published-paper',{'authors':'Author One','abstract':'Published abstract.','publication_status':'Published','year':'2025','paper_url':'https://example.com/paper'}),
    ('activity','Community Workshop','community-workshop',{'type':'Workshop','date':'2025','description':'Published activity.'}),
    ('certificate','Research Credential','research-credential',{'issuer':'Research Society','issue_date':'2025','category':'Research'}),
    ('crest','Service Recognition','service-recognition',{'issuer':'Research Society','date':'2025','description':'Published award details.'}),
    ('gallery','Research Showcase','research-showcase',{'club_id':str(club_id),'date':'2025','caption':'Published event caption.'}),
   ]
   for kind,title,slug,data in records:
    db.execute("INSERT INTO content(kind,title,slug,data,status) VALUES(?,?,?,?,?)",(kind,title,slug,json.dumps(data),'published'))
   db.execute("UPDATE profile SET data=? WHERE id=1",(json.dumps({'email':'contact@example.com'}),))
   db.commit()
  html=self.client.get('/').data.decode()
  for expected in ('career-milestone','project-card searchable','publication-entry','organization-mark','outreach-entry','searchable-credential','trophy-piece','event-card searchable','contactForm','Research Society'):
   self.assertIn(expected,html)
  self.assertIn('data-filter="research" data-filter-target="projects-list"',html)
  self.assertIn('data-filter="research society" data-filter-target="event-grid"',html)
  self.assertIn('A Published Paper',html)
  self.assertIn('mailto:contact@example.com',html)
  self.assertIn('action="/contact"',html); self.assertIn('id="contactForm"',html); self.assertIn('id="contactFeedback"',html)
 def test_media_is_private_until_published_and_survives_edit(self):
  self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'})
  self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  image=BytesIO();Image.new('RGB',(2,2),'teal').save(image,format='PNG');image.seek(0)
  self.client.post('/studio/project/new',data={'title':'Private project','slug':'private-project','status':'draft','sort_order':'0','f_summary':'Visible after publishing','image':(image,'cover.png')},content_type='multipart/form-data')
  with self.app.app_context():
   from portfolio.db import get_db
   row=get_db().execute("SELECT id,data FROM content WHERE slug='private-project'").fetchone()
   item_id=row['id'];filename=json.loads(row['data'])['image_filename']
   media=get_db().execute('SELECT content_id,is_private FROM media WHERE filename=?',(filename,)).fetchone()
   self.assertEqual(media['content_id'],item_id);self.assertEqual(media['is_private'],0)
  with self.client.get('/media/'+filename) as response:self.assertEqual(response.status_code,404)
  preview=self.client.get(f'/studio/preview/project/{item_id}')
  self.assertEqual(preview.status_code,200);self.assertIn(f'/studio/media/{filename}',preview.data.decode())
  with self.client.get('/studio/media/'+filename) as response:self.assertEqual(response.status_code,200)
  self.client.post(f'/studio/project/{item_id}/edit',data={'title':'Private project','slug':'private-project','status':'published','sort_order':'0','f_summary':'Published summary'})
  with self.app.app_context():
   from portfolio.db import get_db
   row=get_db().execute('SELECT data FROM content WHERE id=?',(item_id,)).fetchone()
   self.assertEqual(json.loads(row['data'])['image_filename'],filename)
   self.assertEqual(json.loads(row['data'])['summary'],'Published summary')
  with self.client.get('/media/'+filename) as response:self.assertEqual(response.status_code,200)
  self.assertEqual(self.app.test_client().get('/studio/media/'+filename).status_code,302)
 def test_unsafe_profile_contact_values_are_never_rendered(self):
  with self.app.app_context():
   from portfolio.db import get_db
   get_db().execute("UPDATE profile SET data=? WHERE id=1",(json.dumps({'name':'Portfolio owner','email':'person@example.invalid','phone':'javascript:alert(1)','website':'javascript:alert(2)'}),));get_db().commit()
  html=self.client.get('/').data.decode()
  self.assertIn('mailto:person@example.invalid',html)
  self.assertNotIn('javascript:',html)
 def test_first_admin_setup_and_login(self):
  r=self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'},follow_redirects=True)
  self.assertEqual(r.status_code,200);self.assertIn(b'Welcome back',r.data)
  with self.app.app_context():
   from portfolio.db import get_db
   row=get_db().execute('select password_hash from admins').fetchone();self.assertTrue(check_password_hash(row[0],'very-long-test-password'))
  self.assertEqual(self.client.post('/studio/login',data={'email':'admin@example.com','password':'wrong-password'}).status_code,200)
  self.assertEqual(self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'},follow_redirects=True).status_code,200)
 def test_admin_profile_update_persists(self):
  self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'})
  self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  response=self.client.post('/studio/profile',data={'name':'QA Profile','email':'qa@example.com','phone':'+1 555 0100','theme':'dark'},follow_redirects=True)
  self.assertEqual(response.status_code,200);self.assertIn(b'Profile saved',response.data)
  with self.app.app_context():
   from portfolio.db import get_db
   row=get_db().execute('SELECT data FROM profile WHERE id=1').fetchone()
   saved=json.loads(row['data']);self.assertEqual(saved['name'],'QA Profile');self.assertEqual(saved['email'],'qa@example.com');self.assertEqual(saved['phone'],'+1 555 0100');self.assertEqual(saved['theme'],'dark')
 def test_admin_crud_persists(self):
  self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'})
  self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  r=self.client.post('/studio/project/new',data={'csrf_token':'','title':'Sample Project','slug':'sample-project','status':'published','sort_order':'1','f_summary':'A safe sample'},follow_redirects=True)
  self.assertEqual(r.status_code,200);self.assertIn(b'Sample Project',r.data);self.assertIn(b'Sample Project',self.client.get('/').data)
  self.client.post('/studio/project/1/edit',data={'csrf_token':'','title':'Updated Project','slug':'sample-project','status':'draft','sort_order':'1','f_summary':'Updated'},follow_redirects=True)
  self.assertNotIn(b'Updated Project',self.client.get('/').data)
 def test_anonymous_admin_action_denied(self):
  r=self.client.post('/studio/project/new',data={'title':'Nope'});self.assertEqual(r.status_code,302)
 def test_csrf_rejection_enabled(self):
  app=create_app({'TESTING':True,'DATABASE':self.db,'MEDIA_DIR':self.media,'SECRET_KEY':'test-only-secret','WTF_CSRF_ENABLED':True})
  c=app.test_client();r=c.post('/studio/setup',data={'email':'x@example.com','password':'long-password-123','confirm':'long-password-123'});self.assertEqual(r.status_code,400)
 def test_escaping(self):
  self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'});self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
  self.client.post('/studio/project/new',data={'title':'<script>alert(1)</script>','slug':'xss-test','status':'published','f_summary':'<img src=x onerror=alert(1)>'})
  html=self.client.get('/').data.decode();self.assertNotIn('<script>alert(1)</script>',html);self.assertNotIn('<img src=x onerror=alert(1)>',html)
if __name__=='__main__':unittest.main()

class ContactAndLocationTests(unittest.TestCase):
    def setUp(self):
        import os, tempfile
        from portfolio import create_app
        from portfolio import admin as admin_module
        import portfolio.routes as routes_module
        admin_module.ATTEMPTS.clear(); routes_module.CONTACT_RECENT.clear()
        self.tmp=tempfile.TemporaryDirectory(); base=self.tmp.name
        self.db=os.path.join(base,'test.sqlite3'); self.media=os.path.join(base,'media'); os.makedirs(self.media)
        self.app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'DATABASE':self.db,'MEDIA_DIR':self.media,'SECRET_KEY':'test-only-secret'})
        self.client=self.app.test_client()
    def tearDown(self): self.tmp.cleanup()
    def _setup_login(self):
        self.client.post('/studio/setup',data={'email':'admin@example.com','password':'very-long-test-password','confirm':'very-long-test-password'})
        self.client.post('/studio/login',data={'email':'admin@example.com','password':'very-long-test-password'})
    def test_contact_rejects_too_fast_submission(self):
        r=self.client.post('/contact',data={'name':'A','email':'a@example.com','message':'hello','ts':str(int(__import__('time').time()*1000)),'website_hp':''})
        self.assertEqual(r.status_code,400)
    def test_contact_honeypot_blocked(self):
        import time
        past=time.time()-10
        r=self.client.post('/contact',data={'name':'A','email':'a@example.com','message':'hello','ts':str(past),'website_hp':'http://spam.example'})
        self.assertEqual(r.status_code,400)
    def test_contact_accepts_and_persists(self):
        import time
        past=time.time()-10
        r=self.client.post('/contact',data={'name':'Alice','email':'alice@example.com','message':'Hello there','ts':str(past),'website_hp':''})
        self.assertEqual(r.status_code,200); self.assertTrue(r.json['ok'])
        with self.app.app_context():
            from portfolio.db import get_db
            row=get_db().execute('SELECT name,email,body FROM messages').fetchone()
            self.assertEqual(row['email'],'alice@example.com')
    def test_contact_rate_limited(self):
        import time
        past=str(time.time()-10)
        for _ in range(6):
            r=self.client.post('/contact',data={'name':'Bob','email':'b@example.com','message':'hi','ts':past,'website_hp':''})
        self.assertEqual(r.status_code,429)
    def test_map_hidden_without_location(self):
        html=self.client.get('/').data.decode()
        self.assertNotIn('id="location"',html)
    def test_map_renders_with_openstreetmap_url(self):
        with self.app.app_context():
            from portfolio.db import get_db
            get_db().execute("UPDATE profile SET data=? WHERE id=1",(json.dumps({'location_label':'Dhaka','location_address':'Banani','map_lat':'23.79','map_lng':'90.40','map_url':'https://www.openstreetmap.org/export/embed.html?bbox=90.38%2C23.78%2C90.42%2C23.80'}),)); get_db().commit()
        html=self.client.get('/').data.decode()
        self.assertIn('id="location"',html); self.assertIn('openstreetmap',html)
