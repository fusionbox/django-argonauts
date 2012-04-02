from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User

from reversion.admin import VersionAdmin

from fusionbox.mail import send_markdown_mail

from .models import *


class BlogAdmin(VersionAdmin):
    fieldsets = (
            (None, {
                'fields': ['title', 'author', 'body', 'tags', 'created_at']
                }),
            ('Publishing', {
                'fields': ('publish_at', 'is_published',),
                }),
            ('SEO', {
                'classes': ('collapse',),
                'fields': ['seo_title', 'seo_description', 'seo_keywords'],
                }),
            )
    list_filter = ('is_published',)

admin.site.register(Blog, BlogAdmin)

from django.contrib.comments.moderation import CommentModerator, moderator

class BlogModerator(CommentModerator):
    email_notification = True

    def moderate(self, *args, **kwargs):
        # everything starts private
        return True

    def email(self, comment, content_obj, request):
        send_markdown_mail(
                'blog/comment_notification_email.md',
                {'comment': comment,
                 'blog': content_obj,
                 'request': request},
                (i.email for i in User.objects.filter(is_staff=True)),
                )
        messages.success(request, 'Your comment was submitted for moderation.')

moderator.register(Blog, BlogModerator)
