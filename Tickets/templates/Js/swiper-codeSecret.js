document.addEventListener('DOMContentLoaded', function () {
    if (typeof Swiper === 'undefined') {
        console.error('Swiper is not loaded!');
        return;
    }

    const swiper = new Swiper('.swiper-container', {
        direction: 'horizontal',
        loop: true,
        autoplay: {
            delay: 6000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            dynamicBullets: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
        speed: 1000,
        slidesPerView: 1,
        spaceBetween: 0
    });

    // تولید کد امنیتی تصادفی
    function generateCaptcha() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let captcha = '';
        for (let i = 0; i < 4; i++) {
            captcha += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return captcha;
    }

    // تنظیم کد امنیتی
    const captchaElement = document.querySelector('.captcha-code');
    if (captchaElement) {
        captchaElement.textContent = generateCaptcha();
    }

    console.log('Swiper initialized successfully');
});
