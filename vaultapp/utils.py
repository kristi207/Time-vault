# utils.py or any other logic file
import re
from datetime import datetime, timedelta

def determine_criticality(letter_content):
    urgent_keywords = ['urgent', 'emergency', 'important', 'critical', 'asap']
    priority = 'low'  # Default to low priority

    # Convert content to lowercase for case-insensitive matching
    letter_content = letter_content.lower()

    # Check for urgent keywords
    if any(keyword in letter_content for keyword in urgent_keywords):
        priority = 'high'
    return priority

def determine_time_criticality(letter_send_time):
    urgent_time_window = timedelta(hours=2)
    time_diff = letter_send_time - datetime.now()

    if time_diff < urgent_time_window:
        return 'high'
    return 'low'

def determine_blog_priority(letter):
    if letter.is_public:  # If letter is public, assign higher priority
        return 'high'
    return 'low'

def calculate_combined_priority(letter):
    criticality = determine_criticality(letter.content)
    time_criticality = determine_time_criticality(letter.send_date)
    blog_priority = determine_blog_priority(letter)

    # Assign numeric weights for each factor
    priority_score = 0

    if criticality == 'high':
        priority_score += 3  # High criticality adds more weight
    if time_criticality == 'high':
        priority_score += 2  # Time sensitivity adds weight
    if blog_priority == 'high':
        priority_score += 1  # Blog posts add weight

    # Convert score to priority
    if priority_score >= 5:
        return 'high'
    elif priority_score >= 3:
        return 'medium'
    else:
        return 'low'
