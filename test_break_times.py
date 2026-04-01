"""
Test script to show current time and break availability
Run this to see when breaks are allowed
"""
from datetime import datetime
import pytz

# Get current time in IST
local_tz = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(local_tz)
current_hour = current_time.hour
current_minute = current_time.minute

print("=" * 60)
print("BREAK TIME CHECKER")
print("=" * 60)
print(f"\nCurrent Time (IST): {current_time.strftime('%I:%M %p')}")
print(f"Current Hour: {current_hour}, Current Minute: {current_minute}")
print("\n" + "=" * 60)
print("BREAK SCHEDULE:")
print("=" * 60)
print("1. Morning Tea:   10:00 AM - 11:00 AM")
print("2. Lunch:         1:00 PM - 1:45 PM")
print("3. Evening Tea:   4:00 PM - 4:45 PM")
print("\n" + "=" * 60)
print("CURRENT STATUS:")
print("=" * 60)

# Check morning tea
is_morning_tea = (10 <= current_hour < 11)
print(f"Morning Tea (10-11 AM):  {'✓ AVAILABLE' if is_morning_tea else '✗ Not available'}")

# Check lunch
is_lunch = (current_hour == 13 and current_minute <= 45)
print(f"Lunch (1-1:45 PM):       {'✓ AVAILABLE' if is_lunch else '✗ Not available'}")

# Check evening tea
is_evening_tea = (current_hour == 16 and current_minute <= 45)
print(f"Evening Tea (4-4:45 PM): {'✓ AVAILABLE' if is_evening_tea else '✗ Not available'}")

print("\n" + "=" * 60)
print("NOTE:")
print("=" * 60)
print("- Buttons are DISABLED when not in the allowed time window")
print("- Buttons are ENABLED (with hover effects) during allowed times")
print("- You can take ONE tea break in morning AND ONE in evening")
print("- You can take ONE lunch break per day")
print("=" * 60)
