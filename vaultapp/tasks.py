from django.core.mail import send_mail
from django_q.tasks import async_task
from django.utils.timezone import now
from datetime import timedelta

def send_scheduled_email(sender, recipient, subject, content):
    send_mail(
        subject,
        content,
        sender,
        [recipient],
        fail_silently=False,
    )
