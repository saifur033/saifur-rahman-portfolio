# Free Hosting Notes (বাংলা)

এই ফাইলটি আগে পড়ুন; portfolio-তে admin panel, SQLite database এবং uploaded image/CV আছে। শুধু website online দেখা আর online admin থেকে content স্থায়ীভাবে edit করতে পারা—দুটি আলাদা বিষয়।

## Render Free
- Render-এ Python/Flask web service বিনামূল্যে চালানো যায়।
- Free service 15 মিনিট request না পেলে spin down করতে পারে।
- Free service-এর local filesystem ephemeral: restart, redeploy বা spin-down হলে `instance/portfolio.sqlite3` এবং uploaded media হারাতে পারে।
- তাই database এবং media persistence architecture না বদলে Render Free-তে এই admin CMS deploy করবেন না।
- Official limitations: https://render.com/docs/free

## PythonAnywhere Free
- PythonAnywhere-এ Flask app চালানো যায়, কিন্তু নতুন free account-এর web app এক মাস পর expire হতে পারে; disk, CPU ও outbound internet সীমা রয়েছে।
- এটিকে স্থায়ী hosting guarantee হিসেবে ধরবেন না।
- Official details: https://help.pythonanywhere.com/pages/FreeAccountsFeatures/

## এই project-এর জন্য নিরাপদ পরবর্তী পদক্ষেপ
1. আগে local portfolio design ও tour যাচাই করুন।
2. Hosting provider নির্বাচন করার আগে SQLite database এবং `instance/media/`-এর জন্য persistent storage নিশ্চিত করুন।
3. `PORTFOLIO_SECRET_KEY`-এ দীর্ঘ random secret দিন এবং HTTPS চালু থাকলে `PORTFOLIO_HTTPS=1` সেট করুন।
4. Public deployment-এর আগে default local secret, admin setup, CSRF/session settings, upload access এবং backup/restore পরীক্ষা করুন।
5. Admin credentials, `instance/` database বা private uploads source ZIP/Git repository-তে commit করবেন না।

এই guide কোনো hosting account তৈরি করে না এবং site deploy করে না।
