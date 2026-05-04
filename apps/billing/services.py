"""
Business logic (services) for the billing domain.
Contains functions for transactions, balance updates, and wallet management.
"""
from __future__ import annotations

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, Transaction, TransactionType, TransactionStatus

@transaction.atomic
def create_wallet_for_user(user) -> Wallet:
    """
    Yangi foydalanuvchi uchun hamyon yaratadi.
    Agar hamyon allaqachon mavjud bo'lsa, xatolik beradi.
    """
    # 1. User uchun hamyon bor-yo'qligini tekshiramiz
    if hasattr(user, 'wallet'):
        # Agar hamyon bo'lsa, xatolik qaytaramiz (duplicate oldini olish)
        raise ValidationError(f"User {user.email} allaqachon hamyonga ega.")
    
    # 2. Yangi hamyon yaratamiz
    wallet = Wallet.objects.create(user=user, balance=Decimal('0.00'))
    
    # 3. Yaratilgan hamyonni qaytaramiz
    return wallet

@transaction.atomic
def deposit_to_wallet(wallet: Wallet, amount: Decimal, description: str = "", external_id: str = None) -> Transaction:
    """
    Hamyonni to'ldirish (Deposit).
    Balansni oshiradi va tranzaksiya qayd etadi.
    """
    # 1. Summani tekshiramiz (musbat bo'lishi shart)
    if amount <= 0:
        raise ValidationError("Summa musbat bo'lishi shart.")

    # 2. Hamyon balansini yangilaymiz (F() ifodasidan foydalanish ham mumkin, lekin atomik tranzaksiyadamiz)
    wallet.balance += amount
    wallet.save(update_fields=['balance'])

    # 3. Tranzaksiyani saqlaymiz
    txn = Transaction.objects.create(
        wallet=wallet,
        kind=TransactionType.DEPOSIT,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        description=description or f"Hamyon to'ldirildi: {amount}",
        external_id=external_id
    )

    # 4. Tranzaksiyani qaytaramiz
    return txn

@transaction.atomic
def withdraw_from_wallet(wallet: Wallet, amount: Decimal, description: str = "") -> Transaction:
    """
    Hamyondan pul yechish (Withdraw).
    Agar balans yetarli bo'lmasa, xatolik beradi.
    """
    # 1. Summa va balansni tekshiramiz
    if amount <= 0:
        raise ValidationError("Summa musbat bo'lishi shart.")
    
    if wallet.balance < amount:
        # Pul yetarli bo'lmasa xatolik
        raise ValidationError("Mablag' yetarli emas.")

    # 2. Balansni kamaytiramiz
    wallet.balance -= amount
    wallet.save(update_fields=['balance'])

    # 3. Tranzaksiya tarixini yaratamiz
    txn = Transaction.objects.create(
        wallet=wallet,
        kind=TransactionType.WITHDRAW,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        description=description or f"Hamyondan yechildi: {amount}"
    )

    # 4. Tranzaksiyani qaytaramiz
    return txn

@transaction.atomic
def freeze_funds(wallet: Wallet, amount: Decimal, description: str = "") -> Transaction:
    """
    Mablag'ni muzlatish (Freeze).
    Asosiy balansdan olib, muzlatilgan (frozen) balansga o'tkazadi.
    """
    # 1. Tekshiruvlar
    if amount <= 0:
        raise ValidationError("Summa musbat bo'lishi shart.")
    if wallet.balance < amount:
        raise ValidationError("Muzlatish uchun mablag' yetarli emas.")

    # 2. Balanslarni o'zgartiramiz
    wallet.balance -= amount
    wallet.frozen_balance += amount
    wallet.save(update_fields=['balance', 'frozen_balance'])

    # 3. Tranzaksiyani yaratamiz
    txn = Transaction.objects.create(
        wallet=wallet,
        kind=TransactionType.FREEZE,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        description=description or f"Mablag' muzlatildi: {amount}"
    )

    return txn

@transaction.atomic
def unfreeze_funds(wallet: Wallet, amount: Decimal, description: str = "", to_balance: bool = True) -> Transaction:
    """
    Mablag'ni muzlatishdan chiqarish (Unfreeze).
    to_balance=True bo'lsa asosiy balansga qaytaradi, aks holda shunchaki o'chiradi (to'lov uchun ishlatilganda).
    """
    # 1. Tekshiruv
    if amount <= 0:
        raise ValidationError("Summa musbat bo'lishi shart.")
    if wallet.frozen_balance < amount:
        raise ValidationError("Muzlatilgan balansda yetarli mablag' yo'q.")

    # 2. Muzlatilgan balansdan ayiramiz
    wallet.frozen_balance -= amount
    
    # 3. Agar kerak bo'lsa asosiy balansga qaytaramiz
    if to_balance:
        wallet.balance += amount
    
    wallet.save(update_fields=['balance', 'frozen_balance'])

    # 4. Tranzaksiya
    txn = Transaction.objects.create(
        wallet=wallet,
        kind=TransactionType.UNFREEZE,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        description=description or f"Muzlatishdan chiqarildi: {amount}"
    )

    return txn
