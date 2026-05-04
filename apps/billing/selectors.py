"""
Selectors for the billing domain.
Read-only queries to fetch wallet and transaction information.
"""
from __future__ import annotations

from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import Wallet, Transaction, TransactionStatus

def get_wallet_for_user(user) -> Wallet:
    """
    Foydalanuvchining hamyonini qaytaradi.
    Agar hamyon bo'lmasa, 404 xatolik beradi.
    """
    # get_object_or_404 yordamida hamyonni qidiramiz
    return get_object_or_404(Wallet, user=user)

def get_wallet_balance(user) -> Decimal:
    """
    Foydalanuvchining joriy balansini qaytaradi.
    """
    # Hamyonni olamiz va balans maydonini qaytaramiz
    wallet = get_wallet_for_user(user)
    return wallet.balance

def get_frozen_balance(user) -> Decimal:
    """
    Foydalanuvchining muzlatilgan balansini qaytaradi.
    """
    # Hamyonni olamiz va muzlatilgan balansni qaytaramiz
    wallet = get_wallet_for_user(user)
    return wallet.frozen_balance

def get_user_transaction_history(user, limit: int = 50):
    """
    Foydalanuvchining oxirgi tranzaksiyalar tarixini qaytaradi.
    """
    # 1. User hamyonini olamiz
    wallet = get_wallet_for_user(user)
    
    # 2. Shu hamyonga tegishli barcha tranzaksiyalarni kamayish tartibida olamiz
    return Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:limit]

def get_transaction_by_external_id(external_id: str) -> Transaction | None:
    """
    Tashqi ID (Payme/Click ID) bo'yicha tranzaksiyani topadi.
    """
    # filter().first() ishlatamiz, agar topilmasa None qaytaradi
    return Transaction.objects.filter(external_id=external_id).first()
