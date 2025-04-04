from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, Passenger, Wallet, Category, Event, EventImage, EventDetail
from datetime import date, datetime, timezone
from backend.auth.auth_handler import get_password_hash

db: Session = SessionLocal()

try:
    admin_user = User(
        username="admin",
        password=get_password_hash("admin123"),
        firstname="Admin",
        lastname="User",
        email="admin@example.com",
        is_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(admin_user)
    db.commit()

    passengers = [
        Passenger(user_id=admin_user.id, firstname="محمد", lastname="کاظمی", gender=1, dob=date(1990, 5, 15),
                  national_code="1234567890"),
        Passenger(user_id=admin_user.id, firstname="زهرا", lastname="مرادی", gender=2, dob=date(1995, 8, 22),
                  national_code="2345678901"),
        Passenger(user_id=admin_user.id, firstname="علی", lastname="احمدی", gender=1, dob=date(1988, 3, 10),
                  national_code="3456789012"),
    ]

    db.add_all(passengers)
    db.commit()

    admin_wallet = Wallet(
        user_id=admin_user.id,
        balance=10000000,
        credit_identifier="ABC123DEF456GHI789JKL012"
    )
    db.add(admin_wallet)

    categories = [
        Category(title="تورهای گردشگری"),
        Category(title="تورهای فرهنگی"),
        Category(title="تورهای تاریخی"),
        Category(title="تورهای زیارتی"),
        Category(title="تورهای سیاحتی"),
    ]
    db.add_all(categories)
    db.commit()

    events = [
        Event(
            category_id=1, title="تور کیش ویژه نوروز",
            image="/media/events/kish.jpg", source="تهران", destination="کیش",
            start_date=date(2024, 4, 1), end_date=date(2024, 4, 5),
            price_per_adult=3000000, price_per_child=2000000,
            capacity=20, status=True
        ),
        Event(
            category_id=2, title="تور مشهد",
            image="/media/events/mashhad.jpg", source="تهران", destination="مشهد",
            start_date=date(2024, 5, 10), end_date=date(2024, 5, 15),
            price_per_adult=5000000, price_per_child=3500000,
            capacity=30, status=True
        )
    ]
    db.add_all(events)
    db.commit()

    event_images = [
        EventImage(event_id=1, image_url="/media/event_images/kish_1.jpg"),
        EventImage(event_id=1, image_url="/media/event_images/kish_2.jpg"),
        EventImage(event_id=2, image_url="/media/event_images/mashhad_1.jpg"),
        EventImage(event_id=2, image_url="/media/event_images/mashhad_2.jpg")
    ]
    db.add_all(event_images)
    db.commit()

    event_details = [
        EventDetail(event_id=1, type=1, content="اقامت در هتل ۵ ستاره"),
        EventDetail(event_id=1, type=1, content="صبحانه رایگان"),
        EventDetail(event_id=1, type=2, content="کارت ملی"),
        EventDetail(event_id=1, type=2, content="لباس شنا"),
        EventDetail(event_id=1, type=3, content="عدم استعمال دخانیات در هتل"),
        EventDetail(event_id=1, type=3, content="رعایت ساعت ورود و خروج"),

        EventDetail(event_id=2, type=1, content="پرواز رفت و برگشت"),
        EventDetail(event_id=2, type=1, content="اقامت در هتل ۴ ستاره"),
        EventDetail(event_id=2, type=2, content="پاسپورت معتبر با حداقل ۶ ماه اعتبار"),
        EventDetail(event_id=2, type=2, content="کفش مناسب پیاده‌روی"),
        EventDetail(event_id=2, type=3, content="همراه داشتن بیمه مسافرتی"),
        EventDetail(event_id=2, type=3, content="عدم همراه داشتن حیوانات خانگی")
    ]

    db.add_all(event_details)
    db.commit()

    print("داده‌های نمونه با موفقیت اضافه شدند")

except Exception as e:
    db.rollback()
    print(f"خطا در افزودن داده‌های نمونه: {e}")

finally:
    db.close()
