from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from .models import Letter, PublicLetter, Comment, LetterReaction, BlogPost, BlogInteraction
from unfold.admin import ModelAdmin as UnfoldModelAdmin  # assuming UnfoldModelAdmin is a subclass of admin.ModelAdmin



@admin.register(PublicLetter)
class PublicLetterAdmin(UnfoldModelAdmin):  # Inherit from UnfoldModelAdmin
    list_display = ('title', 'original_letter', 'shared_by', 'is_published', 'shared_date', 'view_count')
    search_fields = ('title', 'description', 'tags', 'nickname', 'original_letter__title', 'shared_by__username')
    list_filter = ('is_published', 'shared_date')
    ordering = ('-shared_date',)
    readonly_fields = ('view_count',)


@admin.register(LetterReaction)
class LetterReactionAdmin(UnfoldModelAdmin):  # Inherit from UnfoldModelAdmin
    list_display = ('user', 'public_letter', 'reacted_at')
    search_fields = ('user__username', 'public_letter__title')
    ordering = ('-reacted_at',)


@admin.register(BlogPost)
class BlogPostAdmin(UnfoldModelAdmin):  # Inherit from UnfoldModelAdmin
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'tags', 'author__username')
    list_filter = ('is_published', 'created_at')
    ordering = ('-created_at',)
    prepopulated_fields = {'title': ('title',)}


@admin.register(Comment)
class CommentAdmin(UnfoldModelAdmin):  # Inherit from UnfoldModelAdmin
    list_display = ('user', 'public_letter', 'created_at')
    search_fields = ('content',)
    ordering = ('-created_at',)


@admin.register(Letter)
class LetterAdmin(UnfoldModelAdmin):  # Inherit from UnfoldModelAdmin
    list_display = ('recipient_email', 'status', 'send_date', 'is_public')
    search_fields = ('recipient_email', 'content')
    list_filter = ('status', 'is_public')
