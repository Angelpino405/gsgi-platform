"""Run once to create the admin account."""
from database import SessionLocal, engine, Base
from auth import hash_password
import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create admin user
existing = db.query(models.User).filter(models.User.username == "angel").first()
if not existing:
    admin = models.User(
        username="angel",
        email="pino.gsgi@gmail.com",
        hashed_password=hash_password("gsgi2024!"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    print("Admin user created: angel / gsgi2024!")
else:
    print("Admin user already exists.")

db.close()
