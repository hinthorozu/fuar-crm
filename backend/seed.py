"""Development seed data for FAIR CRM v0.1.

Run from backend folder:
    python seed.py

Optional reset before seeding:
    python seed.py --reset

This script intentionally uses the existing SQLAlchemy models and keeps all
backend/database names in English. Frontend labels/messages can remain Turkish.
"""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from typing import Iterable

from sqlalchemy import func

from app.database import Base, SessionLocal, engine
from app.models.models import (
    Contact,
    Customer,
    CustomerEmail,
    CustomerPhone,
    Fair,
    FairParticipation,
    ImportBatch,
    ImportRow,
    Note,
    Organization,
    Permission,
    Role,
    RolePermission,
    ScraperRun,
    ScraperSource,
    User,
)
from app.security import hash_password
from app.utils.normalization import (
    normalize_company_name,
    normalize_email,
    normalize_phone,
    normalize_text,
    normalize_website,
)

SEED_RANDOM = 42

PERMISSIONS = [
    ("customer.read", "Read customer records"),
    ("customer.create", "Create customer records"),
    ("customer.update", "Update customer records"),
    ("customer.delete", "Delete customer records"),
    ("fair.read", "Read fair records"),
    ("fair.create", "Create fair records"),
    ("fair.update", "Update fair records"),
    ("fair.delete", "Delete fair records"),
    ("import.run", "Run import previews and imports"),
    ("scraper.run", "Run scraper jobs"),
    ("user.manage", "Manage users and roles"),
]

FAIRS = [
    {
        "fair_name": "WIN Eurasia 2025",
        "organizer": "Hannover Fairs Turkey",
        "venue": "İstanbul Fuar Merkezi",
        "city": "İstanbul",
        "country": "Türkiye",
        "start_date": date(2025, 5, 28),
        "end_date": date(2025, 5, 31),
        "website": "https://www.win-eurasia.com",
    },
    {
        "fair_name": "Maktek Eurasia 2025",
        "organizer": "Tüyap",
        "venue": "Tüyap Fuar ve Kongre Merkezi",
        "city": "İstanbul",
        "country": "Türkiye",
        "start_date": date(2025, 9, 30),
        "end_date": date(2025, 10, 5),
        "website": "https://www.maktekfuari.com",
    },
    {
        "fair_name": "WoodTech 2025",
        "organizer": "RX Tüyap",
        "venue": "Tüyap Fuar ve Kongre Merkezi",
        "city": "İstanbul",
        "country": "Türkiye",
        "start_date": date(2025, 10, 11),
        "end_date": date(2025, 10, 15),
        "website": "https://www.woodtechistanbul.com",
    },
    {
        "fair_name": "Plast Eurasia İstanbul 2025",
        "organizer": "Tüyap",
        "venue": "Tüyap Fuar ve Kongre Merkezi",
        "city": "İstanbul",
        "country": "Türkiye",
        "start_date": date(2025, 12, 3),
        "end_date": date(2025, 12, 6),
        "website": "https://www.plasteurasia.com",
    },
    {
        "fair_name": "Automechanika Istanbul 2025",
        "organizer": "Messe Frankfurt Istanbul",
        "venue": "İstanbul Tüyap",
        "city": "İstanbul",
        "country": "Türkiye",
        "start_date": date(2025, 6, 12),
        "end_date": date(2025, 6, 15),
        "website": "https://automechanika-istanbul.tr.messefrankfurt.com",
    },
]

COMPANY_ROOTS = [
    "ABC Makina", "Delta Otomasyon", "Teknova Elektrik", "Mega Kalıp", "Aras Hidrolik",
    "Nova Robotik", "Atlas Makine", "Kuzey Endüstri", "Beta Metal", "Asya Plastik",
    "Eksen Otomasyon", "Promak CNC", "Akdeniz Pres", "Lider Kalıp", "Global Automation",
    "Sintek Makina", "Optimum Teknoloji", "Marmara Makina", "Elit Endüstri", "Yıldız Teknik Makina",
    "Orion Mekatronik", "Bora Kompresör", "Vizyon Kaynak", "Poyraz Metal", "Ege Robotik",
    "Anka Ambalaj", "Kare Hidrolik", "Zenit Makine", "Form Plastik", "Kromsan Metal",
    "Derin Otomasyon", "Mira Elektronik", "Tuna Endüstri", "Apex Kalıp", "Sembol CNC",
    "Rota Makina", "Netform Plastik", "Alfa Pres", "Teknik Servo", "Mikron Kalıp",
    "Efor Endüstriyel", "Denge Makina", "Smart Line Robotics", "Polen Ambalaj", "Güney Hidrolik",
    "Ritim Elektrik", "Kanyon Metal", "İnova Teknoloji", "Safir Makina", "Ulus Otomasyon",
    "Tasarım Pres", "Metaliksan", "Proline Endüstri", "Vega Plastik", "Nexus Otomasyon",
    "İmaj Makine", "Ekol Kalıp", "Penta Robotik", "Hedef Hidrolik", "Artemis Metal",
    "Turkuaz Elektrik", "Kuzeybatı Makina", "Doğa Plastik", "İdeal CNC", "Ramsan Endüstri",
    "Motto Automation", "Gama Pres", "Kapsam Makina", "Akıllı Robotik", "Fokus Kalıp",
    "Simetri Metal", "Kardelen Plastik", "Eksim Otomasyon", "Mekatek Makina", "Kraft Hidrolik",
    "Sistem Elektronik", "Başak Endüstri", "Avrasya Makina", "Mavi Robotik", "Dinamik CNC",
    "Truva Kalıp", "Metro Metal", "Çelikform Makina", "Yakut Plastik", "Prizma Otomasyon",
    "Neta Makina", "Sentez Hidrolik", "Tekno Pres", "Kale Endüstri", "Mikro Robotik",
    "İstanbul Makine", "Anadolu Kalıp", "Eksenel Metal", "Vektör Elektrik", "Akım Otomasyon",
    "Rulmansan", "Lodos Makina", "Pamir Plastik", "Merkez CNC", "Expo Teknik",
]

CITIES = ["İstanbul", "Bursa", "Kocaeli", "İzmir", "Ankara", "Konya", "Kayseri", "Gaziantep", "Sakarya", "Manisa"]
DISTRICTS = ["İkitelli", "Nilüfer", "Gebze", "Kemalpaşa", "Ostim", "Selçuklu", "Melikgazi", "Şehitkamil", "Arifiye", "Turgutlu"]
TAX_OFFICES = ["İkitelli", "Marmara", "Gebze", "Ege", "Ostim", "Meram", "Erciyes", "Gazikent"]
FIRST_NAMES = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Murat", "Elif", "Sinan", "Zeynep", "Burak", "Deniz", "Emre", "Selin"]
LAST_NAMES = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Arslan", "Aydın", "Koç", "Öztürk", "Kara", "Yıldız", "Aksoy"]
TITLES = ["Satış Müdürü", "İhracat Uzmanı", "Genel Müdür", "Pazarlama Sorumlusu", "Proje Yöneticisi", "Satınalma Yetkilisi"]
DEPARTMENTS = ["Sales", "Export", "Management", "Marketing", "Project", "Purchasing"]


def slugify_domain(company_name: str) -> str:
    normalized = normalize_company_name(company_name) or company_name
    return "".join(ch.lower() for ch in normalized if ch.isalnum())


def chunked(values: Iterable, size: int):
    batch = []
    for value in values:
        batch.append(value)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def reset_database(db) -> None:
    # Child tables first because of FK constraints.
    for model in [
        ScraperRun,
        ScraperSource,
        ImportRow,
        ImportBatch,
        Note,
        CustomerEmail,
        CustomerPhone,
        Contact,
        FairParticipation,
        Customer,
        Fair,
        User,
        RolePermission,
        Permission,
        Role,
        Organization,
    ]:
        db.query(model).delete()
    db.commit()


def ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_auth_foundation(db):
    existing_admin = db.query(User).filter(User.email == "admin@faircrm.local").first()
    if existing_admin:
        if not existing_admin.password_hash:
            existing_admin.password_hash = hash_password("admin123")
        if not existing_admin.is_active:
            existing_admin.is_active = True
        if not existing_admin.role:
            existing_admin.role = "super_admin"
        db.flush()
        return existing_admin

    organization = Organization(
        name="Demo Organization",
        slug="demo",
        is_active=True,
    )
    db.add(organization)
    db.flush()

    super_admin_role = Role(
        organization_id=organization.id,
        name="super_admin",
        description="Full system access for the demo organization.",
        is_active=True,
    )
    db.add(super_admin_role)
    db.flush()

    seeded_permissions = []
    for code, description in PERMISSIONS:
        permission = Permission(code=code, description=description)
        db.add(permission)
        seeded_permissions.append(permission)
    db.flush()

    for permission in seeded_permissions:
        db.add(RolePermission(role_id=super_admin_role.id, permission_id=permission.id))

    admin = User(
        organization_id=organization.id,
        role_id=super_admin_role.id,
        full_name="FAIR CRM Admin",
        email="admin@faircrm.local",
        password_hash=hash_password("admin123"),
        role="super_admin",
        is_active=True,
    )
    db.add(admin)
    db.flush()
    return admin


def seed_fairs(db):
    fairs = []
    for item in FAIRS:
        fair = Fair(**item, normalized_fair_name=normalize_text(item["fair_name"]), is_active=True)
        db.add(fair)
        fairs.append(fair)
    db.flush()
    return fairs


def seed_customers(db):
    customers = []
    for index, root_name in enumerate(COMPANY_ROOTS, start=1):
        legal_suffix = "A.Ş." if index % 3 == 0 else "Ltd. Şti." if index % 3 == 1 else "San. ve Tic. Ltd. Şti."
        company_name = f"{root_name} {legal_suffix}"
        domain = slugify_domain(company_name)
        city_index = (index - 1) % len(CITIES)
        main_phone = f"0212 5{index:02d} {1000 + index:04d}"
        customer = Customer(
            company_name=company_name,
            normalized_company_name=normalize_company_name(company_name),
            website=f"https://www.{domain}.com",
            normalized_website=normalize_website(f"https://www.{domain}.com"),
            main_phone=main_phone,
            normalized_main_phone=normalize_phone(main_phone),
            tax_number=f"{1000000000 + index}",
            tax_office=TAX_OFFICES[index % len(TAX_OFFICES)],
            country="Türkiye",
            city=CITIES[city_index],
            district=DISTRICTS[city_index],
            address=f"Organize Sanayi Bölgesi {index}. Cadde No:{10 + index}",
            description=f"Development seed customer #{index}. CRM ekranları, filtreler ve import karşılaştırmaları için oluşturuldu.",
            source="seed",
            is_active=True,
        )
        db.add(customer)
        customers.append(customer)
    db.flush()
    return customers


def seed_contacts_channels_notes(db, customers, admin):
    for customer_index, customer in enumerate(customers, start=1):
        domain = customer.normalized_website or slugify_domain(customer.company_name) + ".com"
        company_contacts = []
        for contact_offset in range(2):
            first = FIRST_NAMES[(customer_index + contact_offset) % len(FIRST_NAMES)]
            last = LAST_NAMES[(customer_index * 2 + contact_offset) % len(LAST_NAMES)]
            full_name = f"{first} {last}"
            title = TITLES[(customer_index + contact_offset) % len(TITLES)]
            department = DEPARTMENTS[(customer_index + contact_offset) % len(DEPARTMENTS)]
            email = f"{first.lower()}.{last.lower()}@{domain}".replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            phone = f"05{30 + (customer_index % 20)} {200 + customer_index:03d} {10 + contact_offset:02d} {20 + contact_offset:02d}"
            contact = Contact(
                customer_id=customer.id,
                full_name=full_name,
                normalized_full_name=normalize_text(full_name),
                title=title,
                department=department,
                phone=phone,
                email=email,
                note="Seed contact. v0.1 müşteri profil ekranı için.",
                is_primary=contact_offset == 0,
            )
            db.add(contact)
            company_contacts.append(contact)
        db.flush()

        for contact_offset, contact in enumerate(company_contacts):
            db.add(CustomerPhone(
                customer_id=customer.id,
                contact_id=contact.id,
                phone_number=contact.phone,
                normalized_phone=normalize_phone(contact.phone),
                phone_type="mobile",
                label="Primary" if contact_offset == 0 else "Secondary",
                is_primary=contact_offset == 0,
                source="seed",
            ))
            db.add(CustomerEmail(
                customer_id=customer.id,
                contact_id=contact.id,
                email=contact.email,
                normalized_email=normalize_email(contact.email),
                email_type="work",
                label="Primary" if contact_offset == 0 else "Secondary",
                is_primary=contact_offset == 0,
                validation_status="unknown",
                source="seed",
            ))

        db.add(Note(
            customer_id=customer.id,
            contact_id=company_contacts[0].id,
            detail="İlk görüşme yapıldı. Fuar sonrası teklif takibi gerekiyor.",
            note_type="follow_up",
            created_by_user_id=admin.id,
        ))
        if customer_index % 4 == 0:
            db.add(Note(
                customer_id=customer.id,
                detail="Smart Import testleri için eksik telefon/e-posta varyasyonu senaryosunda kullanılabilir.",
                note_type="import_test",
                created_by_user_id=admin.id,
            ))
    db.flush()


def seed_participations(db, customers, fairs):
    random.seed(SEED_RANDOM)
    halls = ["Hall 2", "Hall 3", "Hall 4", "Hall 5", "Hall 6", "Hall 7", "Hall 8", "Hall 9"]
    for index, customer in enumerate(customers, start=1):
        participation_count = 1 + (index % 3)  # 2,3,1 repeating: ~200 records for 100 customers
        selected_fairs = random.sample(fairs, participation_count)
        for fair in selected_fairs:
            hall = halls[(customer.id + fair.id) % len(halls)]
            stand_number = f"{chr(65 + ((customer.id + fair.id) % 6))}{100 + customer.id + fair.id}"
            participation = FairParticipation(
                customer_id=customer.id,
                fair_id=fair.id,
                hall=hall,
                stand_number=stand_number,
                exhibitor_profile_url=f"https://example.com/exhibitors/{fair.id}/{customer.id}",
                external_exhibitor_id=f"SEED-{fair.id:02d}-{customer.id:04d}",
                participation_status="active",
                source="seed",
            )
            db.add(participation)
    db.flush()


def seed_import_preview_samples(db, fairs, customers):
    batch = ImportBatch(
        fair_id=fairs[0].id,
        source_type="excel",
        source_name="development_seed_import_preview",
        original_file_name="win-eurasia-2025-exhibitors-sample.xlsx",
        status="preview_ready",
        total_rows=6,
        successful_rows=0,
        warning_rows=4,
        error_rows=0,
    )
    db.add(batch)
    db.flush()

    samples = [
        (1, "ABC Makina Anonim Şirketi", customers[0], 94.50, "possible_duplicate"),
        (2, "Delta Otomasyon Ltd Şti", customers[1], 91.00, "possible_duplicate"),
        (3, "Teknova Elektrik A.S.", customers[2], 88.75, "possible_duplicate"),
        (4, "Yeni Nesil Robotik Ltd. Şti.", None, None, "new"),
        (5, "Mega Kalip Sanayi Ticaret", customers[3], 86.25, "possible_duplicate"),
        (6, "Atlas Machine Co", None, None, "new"),
    ]

    for row_number, company_name, detected_customer, score, status in samples:
        raw = {
            "company_name": company_name,
            "phone": f"+90 212 700 {row_number:04d}",
            "email": f"info{row_number}@seed-import.local",
            "website": f"https://www.seed-import-{row_number}.com",
            "hall": f"Hall {row_number + 1}",
            "stand_number": f"D{200 + row_number}",
        }
        db.add(ImportRow(
            import_batch_id=batch.id,
            row_number=row_number,
            raw_data_json=raw,
            normalized_data_json={
                "company_name": normalize_company_name(company_name),
                "phone": normalize_phone(raw["phone"]),
                "email": normalize_email(raw["email"]),
                "website": normalize_website(raw["website"]),
            },
            detected_customer_id=detected_customer.id if detected_customer else None,
            match_score=score,
            detection_status=status,
            decision_status="pending",
            warning_message="Benzer firma bulundu; kullanıcı merge/skip/create kararı vermeli." if detected_customer else None,
        ))
    db.flush()


def print_summary(db) -> None:
    models = [Organization, Role, Permission, User, Customer, Contact, CustomerPhone, CustomerEmail, Fair, FairParticipation, Note, ImportBatch, ImportRow]
    print("\nSeed summary")
    print("============")
    for model in models:
        print(f"{model.__tablename__:28s}: {db.query(func.count(model.id)).scalar()}")
    print("\nSample endpoints to test:")
    print("  GET /dashboard/summary")
    print("  GET /customers")
    print("  GET /customers/1/profile")
    print("  GET /fair-participations")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed FAIR CRM development data.")
    parser.add_argument("--reset", action="store_true", help="Delete existing development data before seeding.")
    args = parser.parse_args()

    ensure_tables()
    db = SessionLocal()
    try:
        existing_customers = db.query(func.count(Customer.id)).scalar()
        if existing_customers and not args.reset:
            print(f"Seed skipped: database already has {existing_customers} customers.")
            print("Run `python seed.py --reset` if you want to recreate development data.")
            return

        if args.reset:
            print("Resetting database data...")
            reset_database(db)

        print("Creating seed data...")
        admin = seed_auth_foundation(db)
        fairs = seed_fairs(db)
        customers = seed_customers(db)
        seed_contacts_channels_notes(db, customers, admin)
        seed_participations(db, customers, fairs)
        seed_import_preview_samples(db, fairs, customers)
        db.commit()
        print_summary(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
