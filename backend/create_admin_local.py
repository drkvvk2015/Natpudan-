from app.database import SessionLocal
from app.crud import create_user, get_user_by_email

EMAIL = "admin@admin.com"
PASSWORD = "Admin@123"
FULL_NAME = "Administrator"
ROLE = "admin"


def main():
    db = SessionLocal()
    try:
        existing = get_user_by_email(db, EMAIL)
        if existing:
            print(f"User already exists: {EMAIL} (id={existing.id})")
            return
        user = create_user(db, email=EMAIL, password=PASSWORD, full_name=FULL_NAME, role=ROLE)
        print(f"Created admin user: {user.email} id={user.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
