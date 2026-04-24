#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template.loader import get_template
from django.contrib.auth.models import User

# Test base template
user = User.objects.filter(is_superuser=True).first()
context = {'user': user}

try:
    template = get_template('base.html')
    html = template.render(context)
    print(f"Base template rendered: {len(html)} bytes")
    if len(html) < 100:
        print(f"ERROR: Base template too short!")
        print(html)
    else:
        print("✓ Base template OK")
except Exception as e:
    print(f"ERROR rendering base template: {e}")
    import traceback
    traceback.print_exc()
