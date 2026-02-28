document.addEventListener('DOMContentLoaded', () => {
    // Billing Toggle functionality
    const billingSwitch = document.getElementById('billing-switch');
    const amounts = document.querySelectorAll('.amount');
    const monthlySpan = document.querySelector('.monthly');
    const yearlySpan = document.querySelector('.yearly');

    if (billingSwitch) {
        billingSwitch.addEventListener('change', (e) => {
            const isYearly = e.target.checked;

            if (isYearly) {
                monthlySpan.classList.remove('active');
                yearlySpan.classList.add('active');
            } else {
                monthlySpan.classList.add('active');
                yearlySpan.classList.remove('active');
            }

            // Animate number change
            amounts.forEach(amount => {
                amount.style.opacity = '0';
                setTimeout(() => {
                    if (isYearly) {
                        amount.innerText = amount.getAttribute('data-yearly');
                    } else {
                        amount.innerText = amount.getAttribute('data-monthly');
                    }
                    amount.style.opacity = '1';
                }, 200);
            });
        });
    }

    // Smooth Scrolling for anchored links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(2, 6, 23, 0.95)';
            navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
        } else {
            navbar.style.background = 'rgba(2, 6, 23, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Auth Modals Logic
    const loginBtn = document.querySelector('.login-btn');
    const ctaBtns = document.querySelectorAll('.cta-btn, .primary-btn[href="#pricing"], .outline-btn');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    const closeBtns = document.querySelectorAll('.modal-close');
    const openSignupFromLogin = document.getElementById('openSignupFromLogin');
    const openLoginFromSignup = document.getElementById('openLoginFromSignup');

    // Forms
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginError = document.getElementById('loginError');
    const signupError = document.getElementById('signupError');

    // Open Login Modal
    if (loginBtn) {
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (ApiClient.isAuthenticated()) {
                window.location.href = 'dashboard.html';
                return;
            }
            loginModal.classList.add('active');
        });
    }

    // Open Signup Modal (from pricing buttons)
    ctaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (btn.tagName === 'BUTTON' || btn.getAttribute('href') !== '#pricing' && btn.getAttribute('href') !== '#demo') {
                e.preventDefault();
                if (ApiClient.isAuthenticated()) {
                    window.location.href = 'dashboard.html';
                    return;
                }
                signupModal.classList.add('active');
            }
        });
    });

    // Close Modals
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById(btn.getAttribute('data-close')).classList.remove('active');
        });
    });

    // Switch between modals
    if (openSignupFromLogin) {
        openSignupFromLogin.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.classList.remove('active');
            signupModal.classList.add('active');
        });
    }

    if (openLoginFromSignup) {
        openLoginFromSignup.addEventListener('click', (e) => {
            e.preventDefault();
            signupModal.classList.remove('active');
            loginModal.classList.add('active');
        });
    }

    // Login Submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerText;

            try {
                loginError.style.display = 'none';
                submitBtn.innerText = 'Logging in...';
                submitBtn.disabled = true;

                const email = document.getElementById('loginEmail').value;
                const password = document.getElementById('loginPassword').value;

                await ApiClient.login(email, password);

                // Redirect on success
                window.location.href = 'dashboard.html';
            } catch (err) {
                loginError.innerText = err.message;
                loginError.style.display = 'block';
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Signup Submission
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = signupForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerText;

            try {
                signupError.style.display = 'none';
                submitBtn.innerText = 'Creating account...';
                submitBtn.disabled = true;

                const fullName = document.getElementById('signupName').value;
                const email = document.getElementById('signupEmail').value;
                const password = document.getElementById('signupPassword').value;

                // Register user
                await ApiClient.register({
                    email: email,
                    password: password,
                    full_name: fullName
                });

                // Then auto-login
                await ApiClient.login(email, password);

                // Redirect on success
                window.location.href = 'dashboard.html';
            } catch (err) {
                signupError.innerText = err.message;
                signupError.style.display = 'block';
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
