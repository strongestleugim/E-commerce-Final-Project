import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DEFAULT_SQLITE_PATH = INSTANCE_DIR / "gainz_lab.db"

raw_sqlite_path = os.getenv("SQLITE_DB_PATH")
resolved_sqlite_path = Path(raw_sqlite_path) if raw_sqlite_path else DEFAULT_SQLITE_PATH

if not resolved_sqlite_path.is_absolute():
    resolved_sqlite_path = BASE_DIR / resolved_sqlite_path


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_BYTES", 4 * 1024 * 1024))
    BRAND_NAME = "GAINZ LAB"
    BRAND_TAGLINE = "Engineered Results"
    BRAND_CONTACT = {
        "email": "support@gainzlab.local",
        "phone": "+63 917 555 0148",
        "location": "Metro Manila Demo Fulfillment",
    }
    PREFERRED_CATEGORIES = [
        {
            "name": "Protein",
            "slug": "protein",
            "summary": "Premium blends that support strength goals, daily intake, and post-training recovery.",
        },
        {
            "name": "Pre-Workout",
            "slug": "pre-workout",
            "summary": "Training formulas built to support focus, energy, and high-effort performance.",
        },
        {
            "name": "Creatine",
            "slug": "creatine",
            "summary": "Straightforward creatine options designed to support power output and consistency.",
        },
        {
            "name": "Recovery",
            "slug": "recovery",
            "summary": "Hydration and recovery support for demanding training schedules and repeat sessions.",
        },
        {
            "name": "Bundles",
            "slug": "bundles",
            "summary": "Curated stacks that simplify a strong daily supplement routine.",
        },
        {
            "name": "Accessories",
            "slug": "accessories",
            "summary": "Practical essentials that keep supplements, hydration, and training gear organized.",
        },
    ]
    DEMO_DISCLAIMER = (
        "This is an academic/demo e-commerce project. Product information is for "
        "educational presentation only and does not provide medical advice."
    )
    SQLITE_DB_PATH = str(resolved_sqlite_path)
    PRODUCT_IMAGE_UPLOAD_DIR = str(BASE_DIR / "app" / "static" / "img" / "products" / "uploads")
    PRODUCT_IMAGE_UPLOAD_WEB_PATH = "img/products/uploads"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{resolved_sqlite_path.as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
