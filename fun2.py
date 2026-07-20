from datetime import datetime

print("Enter your birthday:")

try:
    year = int(input("Year (YYYY): "))
    month = int(input("Month (MM): "))
    day = int(input("Day (DD): "))

    birthday = datetime(year, month, day)
    today = datetime.now()

    if birthday > today:
        print("That date is in the future. Please enter a past date.")
    else:
        age_in_days = (today - birthday).days
        print(f"You are {age_in_days} days old.")

except ValueError:
    print("Invalid date. Please enter a real date.")
