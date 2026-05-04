"""
Business logic (services) for the escrow domain.
Coordinates between wallets and orders to ensure secure payments.
"""
from __future__ import annotations

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.billing.services import freeze_funds, unfreeze_funds, deposit_to_wallet
from apps.billing.selectors import get_wallet_for_user
from .models import Escrow, EscrowStatus

@transaction.atomic
def initiate_escrow(order) -> Escrow:
    """
    Escrow jarayonini boshlaydi.
    Xaridorning hamyonidan pulni muzlatadi va Escrow obyektini yaratadi.
    """
    # 1. Xaridor va sotuvchini aniqlaymiz
    buyer = order.user
    seller = order.seller # Order modelida seller maydoni bor deb faraz qilamiz
    amount = order.total_amount

    # 2. Xaridor hamyonini olamiz
    buyer_wallet = get_wallet_for_user(buyer)

    # 3. Billing servisi orqali pulni muzlatamiz
    freeze_funds(
        wallet=buyer_wallet,
        amount=amount,
        description=f"Buyurtma uchun pul muzlatildi: #{order.id}"
    )

    # 4. Escrow obyektini yaratamiz
    escrow = Escrow.objects.create(
        order=order,
        buyer=buyer,
        seller=seller,
        amount=amount,
        status=EscrowStatus.HELD
    )

    return escrow

@transaction.atomic
def release_escrow(escrow: Escrow) -> None:
    """
    Mablag'ni sotuvchiga o'tkazish (Release).
    Xaridorning hamyonidan muzlatilgan pulni butunlay o'chiradi va sotuvchi balansiga qo'shadi.
    """
    if escrow.status != EscrowStatus.HELD:
        raise ValidationError("Faqat ushlab turilgan (HELD) mablag'ni chiqarish mumkin.")

    # 1. Xaridor hamyonidan muzlatilgan pulni yechish (asosiy balansga qaytarmasdan)
    buyer_wallet = get_wallet_for_user(escrow.buyer)
    unfreeze_funds(
        wallet=buyer_wallet,
        amount=escrow.amount,
        description=f"Bitim yakunlandi, pul sotuvchiga yo'naltirildi. Buyurtma: #{escrow.order.id}",
        to_balance=False # Pul xaridorga qaytmaydi, balki tizimdan chiqadi (sotuvchiga o'tadi)
    )

    # 2. Sotuvchi hamyoniga pulni tushirish
    seller_wallet = get_wallet_for_user(escrow.seller)
    deposit_to_wallet(
        wallet=seller_wallet,
        amount=escrow.amount,
        description=f"Buyurtma uchun to'lov qabul qilindi: #{escrow.order.id}"
    )

    # 3. Escrow holatini yangilash
    escrow.status = EscrowStatus.RELEASED
    escrow.save(update_fields=['status'])

@transaction.atomic
def refund_escrow(escrow: Escrow) -> None:
    """
    Mablag'ni xaridorga qaytarish (Refund).
    Muzlatilgan pulni xaridorning asosiy balansiga qaytaradi.
    """
    if escrow.status not in [EscrowStatus.HELD, EscrowStatus.DISPUTED]:
        raise ValidationError("Faqat ushlab turilgan yoki bahsli mablag'ni qaytarish mumkin.")

    # 1. Xaridor hamyonidagi muzlatilgan pulni asosiy balansga qaytarish
    buyer_wallet = get_wallet_for_user(escrow.buyer)
    unfreeze_funds(
        wallet=buyer_wallet,
        amount=escrow.amount,
        description=f"To'lov qaytarildi. Buyurtma: #{escrow.order.id}",
        to_balance=True # Pul xaridorning balansiga qaytadi
    )

    # 2. Escrow holatini yangilash
    escrow.status = EscrowStatus.REFUNDED
    escrow.save(update_fields=['status'])
