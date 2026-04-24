#!/usr/bin/env python
"""Create password reset templates"""

# Password Reset Request Form
password_reset_form = '''{% extends 'base.html' %}
{% load static %}

{% block title %}Reset Password{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-6 col-lg-5">
            <div class="card glass-card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-key fa-3x text-primary mb-3"></i>
                        <h3 class="text-white">Reset Password</h3>
                        <p class="text-muted">Enter your email address and we'll send you a link to reset your password.</p>
                    </div>

                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-4">
                            <label for="email" class="form-label text-white">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" required placeholder="your.email@arraafiinfotech.com">
                        </div>

                        <button type="submit" class="btn btn-primary w-100 py-3">
                            <i class="fas fa-paper-plane me-2"></i>Send Reset Link
                        </button>
                    </form>

                    <div class="text-center mt-4">
                        <a href="{% url 'login' %}" class="text-white" style="text-decoration: none;">
                            <i class="fas fa-arrow-left me-1"></i>Back to Login
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Password Reset Email Sent
password_reset_done = '''{% extends 'base.html' %}
{% load static %}

{% block title %}Password Reset Email Sent{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-6 col-lg-5">
            <div class="card glass-card">
                <div class="card-body p-5 text-center">
                    <i class="fas fa-check-circle fa-4x text-success mb-4"></i>
                    <h3 class="text-white mb-3">Check Your Email</h3>
                    <p class="text-muted mb-4">
                        We've sent you an email with instructions to reset your password. 
                        Please check your inbox and follow the link.
                    </p>
                    <p class="text-muted small mb-4">
                        <i class="fas fa-info-circle me-1"></i>
                        If you don't receive an email within a few minutes, please check your spam folder.
                    </p>
                    <a href="{% url 'login' %}" class="btn btn-primary">
                        <i class="fas fa-arrow-left me-2"></i>Back to Login
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Password Reset Confirm (Set New Password)
password_reset_confirm = '''{% extends 'base.html' %}
{% load static %}

{% block title %}Set New Password{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-6 col-lg-5">
            <div class="card glass-card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-lock fa-3x text-primary mb-3"></i>
                        <h3 class="text-white">Set New Password</h3>
                        <p class="text-muted">Please enter your new password below.</p>
                    </div>

                    {% if validlink %}
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="new_password1" class="form-label text-white">New Password</label>
                            <div class="position-relative">
                                <input type="password" class="form-control" id="new_password1" name="new_password1" required>
                                <span class="position-absolute" id="togglePassword1" style="right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: rgba(255,255,255,0.6); font-size: 1rem;">
                                    <i class="fas fa-eye" id="toggleIcon1"></i>
                                </span>
                            </div>
                        </div>

                        <div class="mb-4">
                            <label for="new_password2" class="form-label text-white">Confirm New Password</label>
                            <div class="position-relative">
                                <input type="password" class="form-control" id="new_password2" name="new_password2" required>
                                <span class="position-absolute" id="togglePassword2" style="right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: rgba(255,255,255,0.6); font-size: 1rem;">
                                    <i class="fas fa-eye" id="toggleIcon2"></i>
                                </span>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary w-100 py-3">
                            <i class="fas fa-check me-2"></i>Reset Password
                        </button>
                    </form>
                    {% else %}
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        This password reset link is invalid or has expired. Please request a new one.
                    </div>
                    <a href="{% url 'password_reset' %}" class="btn btn-primary w-100">
                        <i class="fas fa-redo me-2"></i>Request New Link
                    </a>
                    {% endif %}

                    <div class="text-center mt-4">
                        <a href="{% url 'login' %}" class="text-white" style="text-decoration: none;">
                            <i class="fas fa-arrow-left me-1"></i>Back to Login
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Password visibility toggles
function setupPasswordToggle(toggleId, inputId, iconId) {
    const toggle = document.getElementById(toggleId);
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (toggle && input && icon) {
        toggle.addEventListener('mouseenter', () => toggle.style.color = 'rgba(255,255,255,0.9)');
        toggle.addEventListener('mouseleave', () => toggle.style.color = 'rgba(255,255,255,0.6)');
        
        toggle.addEventListener('click', () => {
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

setupPasswordToggle('togglePassword1', 'new_password1', 'toggleIcon1');
setupPasswordToggle('togglePassword2', 'new_password2', 'toggleIcon2');
</script>
{% endblock %}
'''

# Password Reset Complete
password_reset_complete = '''{% extends 'base.html' %}
{% load static %}

{% block title %}Password Reset Complete{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-6 col-lg-5">
            <div class="card glass-card">
                <div class="card-body p-5 text-center">
                    <i class="fas fa-check-circle fa-4x text-success mb-4"></i>
                    <h3 class="text-white mb-3">Password Reset Successful!</h3>
                    <p class="text-muted mb-4">
                        Your password has been successfully reset. You can now login with your new password.
                    </p>
                    <a href="{% url 'login' %}" class="btn btn-primary btn-lg">
                        <i class="fas fa-sign-in-alt me-2"></i>Login Now
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Email template (plain text)
password_reset_email = '''Hello,

You requested a password reset for your AttendanceHub account.

Click the link below to reset your password:
{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

If you didn't request this, please ignore this email.

This link will expire in 24 hours.

Best regards,
AttendanceHub Team
'''

# Write all templates
import os

# Create registration directory if it doesn't exist
os.makedirs('templates/registration', exist_ok=True)

templates = {
    'templates/registration/password_reset_form.html': password_reset_form,
    'templates/registration/password_reset_done.html': password_reset_done,
    'templates/registration/password_reset_confirm.html': password_reset_confirm,
    'templates/registration/password_reset_complete.html': password_reset_complete,
    'templates/registration/password_reset_email.txt': password_reset_email,
}

for filepath, content in templates.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filepath}")

print("\n✅ All password reset templates created successfully!")
