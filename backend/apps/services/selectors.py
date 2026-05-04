from .models import Service, Booking, BookingStatus
from django.db.models import Count, Q, Subquery, OuterRef


def check_service_availability(service_id: int) -> bool:
    """Tekshirish: Usta hozirda bo'shmı? (TZ §11)"""
    service = Service.objects.filter(id=service_id).first()
    if not service or not service.is_available:
        return False
    # 3 tadan ko'p faol buyurtma → band
    pending_count = Booking.objects.filter(
        service_id=service_id,
        status__in=[BookingStatus.QUEUE, BookingStatus.SCHEDULED, BookingStatus.IN_PROGRESS]
    ).count()
    return pending_count < 3


def get_service_next_slot(service_id: int) -> str:
    """Keyingi bo'sh vaqtni taxmin qilish"""
    pending_count = Booking.objects.filter(
        service_id=service_id,
        status__in=[BookingStatus.QUEUE, BookingStatus.SCHEDULED]
    ).count()
    if pending_count == 0:
        return "Bugun"
    elif pending_count < 2:
        return "Ertaga"
    else:
        return f"{pending_count // 2 + 1} kundan keyin"


def get_service_status_badge(service_id: int) -> dict:
    """
    Usta holati uchun dinamik display ma'lumotlari qaytaradi.
    Template statik matn o'rniga shu funksiyani ishlatadi.

    Returns:
        {
            'available': bool,
            'label': str,          # "MAVJUD" / "BAND"
            'color': str,          # CSS color
            'bg': str,             # CSS background
            'icon': str,           # emoji
            'next_slot': str,      # bo'sh vaqt (faqat band bo'lsa)
        }
    """
    available = check_service_availability(service_id)
    if available:
        return {
            'available': True,
            'label': 'MAVJUD',
            'color': '#166534',
            'bg': '#DCFCE7',
            'border': '#BBF7D0',
            'icon': '✅',
            'next_slot': '',
        }
    return {
        'available': False,
        'label': 'BAND',
        'color': '#92400E',
        'bg': '#FEF3C7',
        'border': '#FDE68A',
        'icon': '⏳',
        'next_slot': get_service_next_slot(service_id),
    }


def get_services_with_status(queryset=None):
    """
    Barcha (yoki berilgan) xizmatlarni faol buyurtma soni bilan annotate qilib qaytaradi.
    N+1 muammosini oldini oladi — bitta DB so'rovi.
    """
    if queryset is None:
        queryset = Service.objects.filter(is_available=True)

    active_bookings = (
        Booking.objects
        .filter(
            service=OuterRef('pk'),
            status__in=[BookingStatus.QUEUE, BookingStatus.SCHEDULED, BookingStatus.IN_PROGRESS]
        )
        .values('service')
        .annotate(cnt=Count('id'))
        .values('cnt')
    )

    return queryset.annotate(
        active_booking_count=Subquery(active_bookings[:1])
    ).order_by('-rating')
