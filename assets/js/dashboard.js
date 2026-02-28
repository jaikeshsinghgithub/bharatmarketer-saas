document.addEventListener('DOMContentLoaded', async () => {
    // 1. Authentication Check
    if (!ApiClient.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const user = await ApiClient.getProfile();

        // Update UI with user info
        document.getElementById('userName').innerText = user.full_name || 'User';
        document.getElementById('userEmail').innerText = user.email;
        if (user.full_name && user.full_name.length > 0) {
            document.getElementById('userInitial').innerText = user.full_name.charAt(0).toUpperCase();
        }
    } catch (err) {
        console.error("Failed to load profile", err);
        window.location.href = 'index.html';
        return;
    }

    // 2. Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', () => {
        ApiClient.removeToken();
        window.location.href = 'index.html';
    });

    // 3. Sidebar Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const panels = document.querySelectorAll('.panel');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class from all
            navItems.forEach(n => n.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            // Add active class to clicked
            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // 4. AI Writer Implementation
    const aiWriterForm = document.getElementById('aiWriterForm');
    const generateBtn = document.getElementById('generateBtn');
    const aiResultBox = document.getElementById('aiResultBox');
    const aiGeneratedContent = document.getElementById('aiGeneratedContent');
    const waMessageContent = document.getElementById('waMessageContent');

    if (aiWriterForm) {
        aiWriterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = document.getElementById('aiPrompt').value;

            const originalHtml = generateBtn.innerHTML;
            generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
            generateBtn.disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/ai/generate-copy`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${ApiClient.getToken()}`
                    },
                    body: JSON.stringify({ prompt: prompt })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to generate copy');
                }

                // Show result
                const content = data.content || data.generated_copy || 'Generated successfully. Edit below:';
                aiGeneratedContent.innerText = content;
                waMessageContent.value = content; // Pre-fill whatsapp field
                aiResultBox.style.display = 'block';

            } catch (err) {
                aiGeneratedContent.innerHTML = `<span style="color: #ff5f56;"><i class="fa-solid fa-triangle-exclamation"></i> ${err.message}</span>`;
                aiResultBox.style.display = 'block';
            } finally {
                generateBtn.innerHTML = originalHtml;
                generateBtn.disabled = false;
            }
        });
    }

    // Copy to clipboard
    document.getElementById('copyResultBtn')?.addEventListener('click', () => {
        navigator.clipboard.writeText(aiGeneratedContent.innerText);
        const btn = document.getElementById('copyResultBtn');
        btn.innerText = 'Copied!';
        setTimeout(() => { btn.innerText = 'Copy'; }, 2000);
    });

    // Move to WhatsApp panel
    document.getElementById('sendToWhatsAppBtn')?.addEventListener('click', () => {
        document.querySelector('[data-target="whatsapp-panel"]').click();
    });

    // 5. Bulk WhatsApp Sender
    const sendBulkBtn = document.getElementById('sendBulkBtn');
    const waStatus = document.getElementById('waStatus');

    if (sendBulkBtn) {
        sendBulkBtn.addEventListener('click', async () => {
            const message = waMessageContent.value;
            if (!message) {
                alert('Please enter a message to send');
                return;
            }

            const checkedContacts = Array.from(document.querySelectorAll('input[name="contacts"]:checked')).map(cb => cb.value);

            if (checkedContacts.length === 0) {
                alert('Please select at least one contact');
                return;
            }

            waStatus.style.display = 'block';
            waStatus.style.background = 'rgba(255,255,255,0.1)';
            waStatus.style.color = 'var(--text-main)';
            waStatus.innerHTML = '<span class="spinner"></span> Sending messages...';
            sendBulkBtn.disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/marketing/whatsapp/send-bulk`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${ApiClient.getToken()}`
                    },
                    body: JSON.stringify({
                        message: message,
                        numbers: checkedContacts
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to send messages');
                }

                waStatus.style.background = 'rgba(39, 201, 63, 0.2)';
                waStatus.style.color = '#27c93f';
                waStatus.innerHTML = '<i class="fa-solid fa-check"></i> Messages queued successfully!';

                // Reset after 3 seconds
                setTimeout(() => {
                    waStatus.style.display = 'none';
                }, 3000);

            } catch (err) {
                waStatus.style.background = 'rgba(255, 95, 86, 0.2)';
                waStatus.style.color = '#ff5f56';
                waStatus.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Error: ' + err.message;
            } finally {
                sendBulkBtn.disabled = false;
            }
        });
    }

    // 6. Payment & Upgrade Flow
    const upgradeBtns = document.querySelectorAll('a[href="#"]'); // Captures topbar upgrade link
    upgradeBtns.forEach(btn => {
        if (btn.innerText.includes('Upgrade')) {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const originalText = btn.innerText;
                btn.innerText = 'Redirecting...';

                try {
                    // Call the backend to create a razorpay subscription link
                    const response = await fetch(`${API_BASE_URL}/payments/create-razorpay-subscription?plan_key=growth_inr`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${ApiClient.getToken()}`
                        }
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to initialize payment');
                    }

                    if (data.subscription_id) {
                        // Launch Razorpay Checkout
                        const options = {
                            "key": "YOUR_RAZORPAY_KEY_ID", // Replace in production or fetch from backend env
                            "subscription_id": data.subscription_id,
                            "name": "BharatMarketer SaaS",
                            "description": "Growth Plan Upgrade",
                            "image": "https://dummyimage.com/150x150/000/fff&text=BM",
                            "handler": function (response) {
                                alert("Payment successful! Your account is now being upgraded. Subscription ID: " + response.razorpay_subscription_id);
                                // The backend webhook will handle enabling the user's features
                                setTimeout(() => window.location.reload(), 3000);
                            },
                            "theme": {
                                "color": "#FF7A00"
                            }
                        };
                        const rzp1 = new Razorpay(options);
                        rzp1.on('payment.failed', function (response) {
                            alert("Payment Failed. Reason: " + response.error.description);
                        });
                        rzp1.open();
                    } else if (data.short_url) {
                        window.location.href = data.short_url; // Redirect to Razorpay checkout page fallback
                    } else {
                        alert('Payment link not received.');
                    }
                } catch (err) {
                    alert('Integration Error: ' + err.message + '\\nNote: Requires real Razorpay API keys in .env');
                } finally {
                    btn.innerText = originalText;
                }
            });
        }
    });

});
