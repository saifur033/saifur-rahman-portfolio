"""Build a clean source ZIP, excluding local secrets, databases, uploads and environments."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
out = root.parent / "saifur-rahman-portfolio-v3.zip"
excluded_dirs = {
    ".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__",
    "env", "instance", "media", "node_modules", "private_uploads",
    "uploads", "venv",
}
excluded_suffixes = {
    ".cer", ".crt", ".db", ".der", ".key", ".log", ".pem", ".p12",
    ".pfx", ".pyc", ".sqlite", ".sqlite3",
}
excluded_names = {"credentials.json", "secrets.json", "id_rsa", "id_ed25519"}

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.lower() in excluded_dirs for part in relative.parts):
            continue
        if (
            path.name.lower().startswith(".env")
            or path.name.lower() in excluded_names
            or path.suffix.lower() in excluded_suffixes
        ):
            continue
        archive.write(path, Path("saifur-rahman-portfolio-v3") / relative)

print(out)
