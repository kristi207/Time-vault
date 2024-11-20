from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Letter(models.Model):
    # Linking the letter to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='letters', null=True, blank=True)
    # Email for anonymous or registered users
    recipient_email = models.EmailField()
    # The letter content
    content = models.TextField()
    # The date to send the letter
    send_date = models.DateTimeField()
    # Status of the letter (e.g., scheduled, sent)
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    # Whether the letter is publicly viewable
    is_public = models.BooleanField(default=False)
    # Title for the letter (optional for public readability)
    title = models.CharField(max_length=255, null=True, blank=True)
    # Date when the letter was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Last updated date
    updated_at = models.DateTimeField(auto_now=True)

    def is_future_date(self):
        """Ensure the send date is in the future."""
        return self.send_date > now()

    def __str__(self):
        return f"Letter to {self.recipient_email} scheduled for {self.send_date}"

class PublicLetter(models.Model):
    # Linking to the original letter
    original_letter = models.OneToOneField(
        'Letter', on_delete=models.CASCADE, related_name='public_letter'
    )
    # User who shared the letter publicly
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # A nickname or pseudonym for the public letter
    nickname = models.CharField(max_length=100, null=True, blank=True)
    # Blog-specific fields
    title = models.CharField(max_length=255, null=True, blank=True)  # Blog title
    description = models.TextField(null=True, blank=True)  # Blog description/introduction
    tags = models.CharField(max_length=255, null=True, blank=True)  # Comma-separated tags
    # Feature photo for the public letter/blog
    feature_photo = models.ImageField(upload_to='public_letters/photos/', null=True, blank=True)
    # Date when the letter was made public
    shared_date = models.DateTimeField(auto_now_add=True)
    # Whether the blog is active/published
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"Public Letter: {self.title or self.original_letter.title or 'The Letter From {self.shared_date}'}"


class LetterReaction(models.Model):
    # Linking the reaction to a public letter
    public_letter = models.ForeignKey(PublicLetter, on_delete=models.CASCADE, related_name='reactions')
    # Type of reaction (e.g., like, love, etc.)
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('inspired', 'Inspired'),
        ('wow', 'Wow'),
    ]
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    # User who reacted (optional for anonymous reactions)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Date of the reaction
    reacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reaction_type} by {self.user or 'Anonymous'} on {self.public_letter}"

class Comment(models.Model):
    # Linking the comment to a public letter
    public_letter = models.ForeignKey(PublicLetter, on_delete=models.CASCADE, related_name='comments')
    # User who wrote the comment
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # The content of the comment
    content = models.TextField()
    # Timestamp when the comment was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional field for replying to another comment
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user or 'Anonymous'} on {self.public_letter}"