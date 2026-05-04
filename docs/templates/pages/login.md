# Template: pages/login.html (o'zgarish)

## Fayl: `backend/templates/pages/login.html`

## O'zgarish
JavaScript qismida redirect mantiqi o'zgartirildi.

###olding
`window.location.href = '/'` — har doim bosh sahifaga yo'naltirardi.

###Yangi
API javobidan qaytarilgan `response.redirect` qiymatidan foydalaniladi:
```js
const redirectUrl = response.redirect || '/';
setTimeout(() => {
    window.location.href = redirectUrl;
}, 1000);
```

## Maqsad
Mijozlar login dan so'ng profil sahifasiga (`/profile/`), adminlar esa admin panelga yo'naltiriladi. Bu logika backend (TokenView) da `response.data['redirect']` orqali qo'yiladi.

## Eslatma
Shuningdek, login form maydoni "email" nomi saqlanib qolgan, lekin backend endi telefon raqamini ham qabul qiladi (auth_methods/serializers.py da o'zgartirish).