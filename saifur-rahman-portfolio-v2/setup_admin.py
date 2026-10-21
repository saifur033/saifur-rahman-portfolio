"""Optional interactive CLI to create the first admin account."""
import getpass, re
from werkzeug.security import generate_password_hash
from app import app
from portfolio.db import get_db
with app.app_context():
 db=get_db()
 if db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]:
  print("An admin account already exists. Use the web login or reset it manually after a verified backup.")
 else:
  email=input("Admin email: ").strip().lower(); password=getpass.getpass("Password (12+ characters): "); confirm=getpass.getpass("Confirm password: ")
  if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(password)<12 or password!=confirm: raise SystemExit("Invalid email or passwords do not match / are too short.")
  db.execute("INSERT INTO admins(email,password_hash) VALUES(?,?)",(email,generate_password_hash(password)));db.commit();print("Admin created. Start the app and sign in at /studio/login.")
