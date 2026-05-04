"""
Django admin registration for the billing domain.
Allows administrators to manage wallets and view transaction logs.
"""
from __future__ import annotations

from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Hamyonlarni boshqarish uchun admin interfeysi.
    """
    # Ro'yxatda ko'rinadigan ustunlar
    list_display = ("user", "balance", "frozen_balance", "is_active", "created_at")
    
    # Filtrlash imkoniyatlari
    list_filter = ("is_active", "created_at")
    
    # Qidiruv maydonlari (email yoki username bo'yicha)
    search_fields = ("user__email", "user__username")
    
    # Faqat o'qish mumkin bo'lgan maydonlar (xavfsizlik uchun balansni qo'lda o'zgartirish cheklanishi mumkin)
    readonly_fields = ("created_at", "updated_at")
    
    # Tartiblash
    ordering = ("-created_at",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Tranzaksiyalar tarixini kuzatish uchun admin interfeysi.
    Tranzaksiyalar odatda o'zgartirilmaydi (immutable), shuning uchun ko'p maydonlar readonly bo'lishi kerak.
    """
    # Ro'yxatda ko'rinadigan ustunlar
    list_display = ("wallet", "kind", "amount", "status", "external_id", "created_at")
    
    # Filtrlash
    list_filter = ("kind", "status", "created_at")
    
    # Qidiruv
    search_fields = ("wallet__user__email", "external_id", "description")
    
    # Tranzaksiyalar tarixini o'zgartirish xavfli, shuning uchun ko'pini readonly qilamiz
    readonly_fields = ("wallet", "kind", "amount", "status", "external_id", "meta_data", "created_at", "updated_at")
    
    # Yangi tranzaksiyani qo'shish tugmasini o'chirib qo'yish ham mumkin (faqat tizim orqali yaratilishi uchun)
    # def has_add_permission(self, request): return False

    ordering = ("-created_at",)
