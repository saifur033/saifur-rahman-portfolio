# Saifur Rahman Portfolio v2 — Design Refresh (বাংলা)

এটি Flask + SQLite দিয়ে তৈরি একটি local portfolio এবং private admin studio। প্রথমবার চালানোর আগে Python 3.11 বা নতুন compatible Python ইনস্টল থাকতে হবে। VS Code ও Windows Terminal ব্যবহার করুন। কোনো paid API বা hosting দরকার নেই।

## ১. চালু করুন
1. ZIP extract করুন। `saifur-rahman-portfolio` project folder খুলুন।
2. `START.bat`-এ double-click করুন। এটি নিজের project folder-এ গিয়ে `.venv`-এর Python দিয়ে app চালায়। প্রথমবার virtual environment তৈরি এবং `requirements.txt`-এর packages install হবে; internet লাগবে শুধু Python packages install করার সময়।
3. Terminal-এ `Use this exact address in your browser`-এর পর দেখানো URL খুলুন। App প্রথমে port 5000 নেয়; সেটি ব্যস্ত থাকলে 5001–5010-এর মধ্যে প্রথম খালি port ব্যবহার করে। তাই 5001 সবসময় সঠিক নয়—চলমান Flask server যে port ব্যবহার করছে, URL-এ সেই port-ই ব্যবহার করুন।
4. Terminal-এর URL-এর শেষে `/studio` যোগ করে admin খুলুন। প্রথমবার **Create your private admin account** পেজ আসবে। নিজের email এবং অন্তত ১২ অক্ষরের password দিন। কোনো default password নেই।

`START.bat`-এর বদলে PowerShell-এ manually চালাতে project folder-এ গিয়ে `.\.venv\Scripts\python.exe app.py` চালান; এতে default port 5000 ব্যবহার হবে। অন্য port চাইলে আগে `$env:PORT = "5001"` সেট করে একই command চালান এবং সেই port-ই খুলুন। startup error হলে terminal-এর traceback দেখুন; dependency error হলে `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` চালান। Flask app-এ project root-এর `templates/` ও `static/` ব্যবহার করা হয়।

## ২. Content যোগ করুন
Studio Overview থেকে Profile & Appearance খুলে নিজের degree/university, role, contact, About এবং welcome text edit করুন। অন্য section-এ Add record চাপুন। নতুন item default-এ Draft থাকবে; যাচাই করে Published নির্বাচন করে Save করুন। Draft/Hidden item public site-এ দেখাবে না। Delete করার আগে confirmation আসবে।

## ৩. Upload
Image JPEG, PNG, WEBP বা GIF হতে হবে এবং সর্বোচ্চ 8 MB। Certificate-এ valid PDF নেওয়া যায়। Image content যাচাই করে WEBP-তে convert হয়। Upload-এর original filename public URL হিসেবে ব্যবহার হয় না। CV হিসেবে PDF দিন।

## ৪. Database ও backup
Database `instance/portfolio.sqlite3`-এ এবং media `instance/media/`-এ থাকে। এগুলো source ZIP-এ থাকে না। Backup করতে app বন্ধ করে দুটোই নিরাপদ স্থানে copy করুন। Database schema `CREATE TABLE IF NOT EXISTS` দিয়ে initialize হয়; প্রতিবার চালু হলে data reset হয় না।

## ৫. 3D ও internet dependency
Design refresh v2-তে reception-এ আলাদা tour guide ও কম্পিউটারে কাজ করা seated receptionist, black-marble countertop, walnut slats, brass details ও warm LED lighting যোগ করা হয়েছে। Bronze-frame glass partitions-এর পেছনে About & Career, Projects, Publications, Outreach, Certificates, Trophy, Gallery এবং Contact-এর জন্য আলাদা procedural room interior ও sign আছে; hinged glass doors, camera follow এবং guided entry-ও আছে। Room ও character-গুলো stylized procedural geometry—photoreal model বা rigged cartoon নয়। WebGL unavailable হলে accessible HTML fallback ও room buttons থাকে। Three.js `0.180.0` jsDelivr CDN এবং Google Fonts-এর জন্য internet দরকার; system font fallback আছে। কোনো audio autoplay নেই। Browser local storage-এ theme এবং shortlist রাখা হয়।

## ৬. Free hosting নিয়ে গুরুত্বপূর্ণ কথা
এই project-এর admin panel SQLite database এবং uploaded media-তে content সংরক্ষণ করে। Render Free web service idle হলে sleep করে এবং তার local filesystem (SQLite database ও uploaded media-সহ) restart, redeploy বা spin-down হলে হারিয়ে যায়; তাই database/storage পরিবর্তন ছাড়া সেখানে live admin CMS deploy করা নিরাপদ নয়। PythonAnywhere-এর নতুন free accounts-এ web app এক মাস পর expire হতে পারে এবং disk/CPU সীমা আছে। দীর্ঘমেয়াদে সত্যিকারের free hosting চাইলে database ও media-র persistence সমাধান আগে বেছে নিতে হবে। এই ZIP কোনো hosting account তৈরি বা deploy করে না।

## ৭. Security ও limitations
- CSRF protection, password hashing, login attempt limiting, authenticated admin routes, random media names এবং content-based upload validation আছে।
- `PORTFOLIO_SECRET_KEY` না থাকলে প্রতিবার app চালুর সময় random local key তৈরি হয়; restart-এর পরে আবার admin login করতে হতে পারে। Deployment-এর জন্য স্থায়ী secret key environment variable-এ দিন এবং HTTPS হলে `PORTFOLIO_HTTPS=1` করুন। Public deployment security review ছাড়া করবেন না।
- Login limiting process-local; app restart হলে limit history reset হয়।
- Admin content editor common fields ব্যবহার করে; full relational editor/page builder drag-and-drop, multilingual per-field editor, offline bundled Three.js, map tiles, multi-image albums, complex section ordering, full media ownership workflow এবং complete club/crest relational dropdown UI এখনো সম্পূর্ণ নয়। Club/crest relation `club_id` field দিয়ে দেওয়া যায়, কিন্তু এটি validated dropdown নয়—তাই requirements-এর crest-linking UX পুরোপুরি পূরণ হয়েছে বলা যাবে না।
- Location map intentionally omitted because no verified coordinates or offline map dataset was supplied. Latitude/longitude fields can be saved but are not rendered as a map.
- Public email/phone/social links are optional; no fake contact form or booking button exists.

## ৮. Tests
`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` চালান। Test suite local temporary database ব্যবহার করে। ZIP তৈরির আগে tests চালানোর চেষ্টা করুন; result report conversation-এ দেওয়া হবে।

## ৯. Clean source ZIP
`package_source.py` চালালে project root-এর পাশে `saifur-rahman-portfolio-v3.zip` তৈরি হয়। ZIP-এ virtual environment, database, `.env` secrets, private uploads এবং key/certificate files রাখা হয় না।


## 3D tour এবং accessibility
- Hero/scene styling polished with warm ivory, navy, teal, restrained oak/brass and responsive layout.
- The separate procedural tour guide walks to each of eight labeled rooms; the receptionist stays seated at reception. Glass room partitions, hinged doors, camera follow, room navigation, and reduced-motion support are included.
- Quick View is an accessible dialog. Contact details are shown only when entered in the private profile editor; no sample career claims or public default contact details are added.
- Three.js 0.180.0 remains a pinned CDN dependency; no bundled Three.js source is included. If the CDN or WebGL is unavailable, the room buttons and public content remain accessible without 3D.
- Check the current build with `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Database records and uploads are preserved on disk and excluded from the source ZIP.
