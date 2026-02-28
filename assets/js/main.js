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
});
