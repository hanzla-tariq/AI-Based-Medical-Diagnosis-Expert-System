"""
ShifaBot - Admin User Seeder

Creates the default admin account if it doesn't already exist.
This runs automatically on app startup via create_app().
"""

ADMIN_EMAIL = 'hanzlasial690@gmail.com'
ADMIN_PASSWORD = '654321'
ADMIN_NAME = 'Admin'
ADMIN_ROLE = 'admin'


def seed_admin(app):
    """Create admin user if not already present. Called inside create_app()."""
    from .extensions import db
    from .models.user import User

    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        # Ensure role and is_active are correct
        if existing.role != 'admin':
            existing.role = 'admin'
        if not existing.is_active:
            existing.is_active = True
        db.session.commit()
        return

    admin = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        role=ADMIN_ROLE,
        is_active=True
    )
    admin.set_password(ADMIN_PASSWORD)

    db.session.add(admin)
    db.session.commit()
    print(f'[ShifaBot] Admin account created: {ADMIN_EMAIL}')
