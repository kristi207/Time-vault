from django.contrib import admin
from .models import Letter, PublicLetter, Comment, LetterReaction, BlogPost



admin.site.register(PublicLetter)
admin.site.register(LetterReaction)
admin.site.register(BlogPost)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'public_letter', 'created_at')
    search_fields = ('content',)
    ordering = ('-created_at',)

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'status', 'send_date', 'is_public')
    search_fields = ('recipient_email', 'content')
    list_filter = ('status', 'is_public')
    
