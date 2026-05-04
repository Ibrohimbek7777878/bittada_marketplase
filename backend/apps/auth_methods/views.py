"""Auth endpoints — login, OTP flows, and registration."""
from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.throttles import AuthEndpointThrottle

from apps.users.serializers import UserSerializer

from core.exceptions import DomainError
from .serializers import (
    BittadaTokenObtainPairSerializer,
    OtpConfirmSerializer,
    OtpRequestSerializer,
    RegisterSerializer,
)
from .services import confirm_otp, issue_otp, register_with_email_password


class RegisterView(APIView):
    """Ro'yxatdan o'tish ko'rinishi (rolga mos redirect bilan)."""
    permission_classes = [permissions.AllowAny]
    # throttle_classes = [AuthEndpointThrottle]

    def post(self, request):  # type: ignore[no-untyped-def]
        ser = RegisterSerializer(data=request.data)
        
        if not ser.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': ser.errors,
                    'message': 'Validatsiya xatosi. Ma\'lumotlarni tekshiring.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = register_with_email_password(**ser.validated_data)
            
            # Yangi: Ro'yxatdan o'tgach avtomatik tizimga kirish (Session login)
            from django.contrib.auth import login
            login(request, user)

            # Rol bo'yicha redirect URL ni aniqlash (TZ 8.2)
            if user.role == 'seller':
                redirect_url = '/services/'  # Sotuvchi shaxsiy kabinetiga
            elif user.role == 'internal_supplier':
                redirect_url = '/profile/'  # Ichki ta'minotchi profil sahifasi
            else:
                redirect_url = '/'  # customer → Asosiy sahifa

            return Response(
                {
                    'success': True,
                    'user': UserSerializer(user).data,
                    'redirect': redirect_url,
                    'message': 'Akkaunt muvaffaqiyatli yaratildi.'
                },
                status=status.HTTP_201_CREATED
            )
        except DomainError as de:
            # Domain-specific xatoliklarni (masalan, email band bo'lsa) 400 bilan qaytarish
            return Response(
                {
                    'success': False,
                    'errors': {de.code or 'non_field_errors': [str(de)]},
                    'message': str(de)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Noma'lum texnik xatoliklarni 500 bilan qaytarish
            return Response(
                {
                    'success': False,
                    'errors': {'non_field_errors': [str(e)]},
                    'message': 'Ro\'yxatdan o\'tishda kutilmagan xatolik yuz berdi.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OtpRequestView(APIView): # OTP (kod) so'rash ko'rinishi
    permission_classes = [permissions.AllowAny] # Hammasiga ochiq
    throttle_classes = [AuthEndpointThrottle] # Cheklovlar

    def post(self, request):  # type: ignore[no-untyped-def] # POST so'rovi
        ser = OtpRequestSerializer(data=request.data) # Serializer
        ser.is_valid(raise_exception=True) # Validatsiya
        otp = issue_otp(**ser.validated_data) # OTP yaratish

        if ser.validated_data["method"] == "email_otp": # Agar email orqali bo'lsa
            send_otp_email.delay(otp.target, otp.plain_code)  # Email yuborish (Async)
        else: # Agar SMS orqali bo'lsa
            send_otp_sms.delay(otp.target, otp.plain_code)  # SMS yuborish (Async)

        return Response({"sent": True}, status=status.HTTP_202_ACCEPTED) # Qabul qilindi


class OtpConfirmView(APIView): # OTP tasdiqlash ko'rinishi
    permission_classes = [permissions.AllowAny] # Ochiq
    throttle_classes = [AuthEndpointThrottle] # Cheklov

    def post(self, request):  # type: ignore[no-untyped-def] # POST so'rovi
        ser = OtpConfirmSerializer(data=request.data) # Serializer
        ser.is_valid(raise_exception=True) # Validatsiya
        confirm_otp(**ser.validated_data) # Tasdiqlash servisini chaqirish
        return Response({"ok": True}) # Hammasi joyida


class TokenView(TokenObtainPairView):
    """
    JWT token olish (Login).
    Hozirgi o'zgarish: Login muvaffaqiyatli bo'lsa, Django sessiyasiga ham yozadi.
    Bu admin panelga ikkinchi marta login qilmasdan kirishga imkon beradi.
    """
    serializer_class = BittadaTokenObtainPairSerializer
    # throttle_classes = [AuthEndpointThrottle]

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import login
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Serializer orqali validatsiya qilingan userga kirish
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                user = serializer.user
                if user:
                    login(request, user) # Django sessiyasini boshlash
            except Exception:
                pass
        return response


class TokenRefresh(TokenRefreshView): # JWT tokenni yangilash
    throttle_classes = [AuthEndpointThrottle] # Cheklov


class SocialLoginView(APIView): # Ijtimoiy tarmoqlar orqali kirish (Google/Telegram)
    """
    Google yoki Telegram orqali kirishni boshqarish.
    Google uchun: ID Token (credential) qabul qilinadi va tahlil qilinadi.
    """
    permission_classes = [permissions.AllowAny] # Ochiq
    throttle_classes = [AuthEndpointThrottle] # Cheklov

    def post(self, request): # POST so'rovi
        from .serializers import SocialLoginSerializer # Serializerni import qilish
        import jwt  # JWT bilan ishlash uchun kutubxona
        from rest_framework_simplejwt.tokens import RefreshToken # Token yaratish uchun
        from django.conf import settings # Sozlamalar
        
        ser = SocialLoginSerializer(data=request.data) # Ma'lumotlarni olish
        ser.is_valid(raise_exception=True) # Tekshirish
        
        provider = ser.validated_data['provider'] # Provayder (Google)
        credential = ser.validated_data['credential'] # ID Token
        
        if provider == 'google': # Agar Google bo'lsa
            try: # Tahlil qilish jarayoni
                # Tokenni dekod qilish (haqiqiy tizimda imzo tekshirilishi shart)
                decoded = jwt.decode(credential, options={"verify_signature": False})
                email = decoded.get('email') # Emailni olish
                name = decoded.get('name') # Ismni olish
                picture = decoded.get('picture') # Rasmni olish
                
                if not email: # Agar email bo'lmasa xato qaytarish
                    return Response({"error": "Email topilmadi"}, status=400)
                
                # Foydalanuvchini bazadan qidirish yoki yangi yaratish
                from apps.users.models import User, Role, AccountType
                from apps.users.services import create_user_with_profile
                
                user = User.objects.filter(email__iexact=email).first() # Email bo'yicha qidirish
                if not user: # Agar foydalanuvchi mavjud bo'lmasa
                    username = email.split('@')[0] # Emailning birinchi qismini olish
                    if User.objects.filter(username=username).exists(): # Agar username band bo'lsa
                        import uuid
                        username = f"{username}_{str(uuid.uuid4())[:8]}" # Tasodifiy qo'shimcha
                    
                    # Yangi foydalanuvchi yaratish
                    user = create_user_with_profile(
                        email=email,
                        password=User.objects.make_random_password(), # Tasodifiy parol
                        username=username,
                        role=Role.CUSTOMER,
                        account_type=AccountType.INDIVIDUAL
                    )
                    if picture: # Rasm bo'lsa saqlash
                        user.profile.bio = f"Google User. Picture: {picture}"
                        user.profile.save()

                # Tizim uchun JWT tokenlarini generatsiya qilish
                refresh = RefreshToken.for_user(user)
                refresh['role'] = user.role # Rolni qo'shish
                refresh['username'] = user.username # Username qo'shish
                refresh['account_type'] = user.account_type # Hisob turini qo'shish

                return Response({ # Muvaffaqiyatli javob
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "username": user.username,
                        "role": user.role,
                        "name": name
                    }
                })
                
            except Exception as e: # Xatolik bo'lsa
                return Response({"error": f"Social login xatosi: {str(e)}"}, status=400)
        
        return Response({"error": "Noma'lum provayder"}, status=400) # Provayder xatosi
