from django.views.generic import (ListView, DetailView)
from django.core.cache import cache
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from tagging.models import Tag

from .models import Blog


class WithTagMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(WithTagMixin, self).get_context_data(*args, **kwargs)
        context['tags'] = Tag.objects.all()
        return context

class BlogContextMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BlogContextMixin, self).get_context_data(*args, **kwargs)
        # lambda makes it lazy
        context['blogs_for_left_nav'] = lambda: Blog.objects.published().year_month_groups()
        context['blogs_cache_version'] = lambda: cache.get('fusionbox.blog.all_blogs.version')
        return context


class IndexView(WithTagMixin, BlogContextMixin, ListView):
    model = Blog
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = Blog.objects.published().order_by('-created_at').select_related('author')
        try:
            qs = qs.search(self.request.GET['search'])
        except KeyError:
            pass
        try:
            qs = qs.filter(author__id = self.kwargs['author_id'])
        except KeyError:
            pass

        # this must go last, the tagged manager returns a different queryset
        try:
            qs = self.model.tagged.with_all([self.kwargs['tag']], qs)
        except KeyError:
            pass

        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        try:
            context['tag'] = get_object_or_404(Tag, name=self.kwargs['tag'])
        except KeyError:
            pass
        try:
            context['author'] = get_object_or_404(User, id=self.kwargs['author_id'])
        except KeyError:
            pass
        return context

index = IndexView.as_view(template_name="blog/blog_list.html")


class BlogDetailView(WithTagMixin, BlogContextMixin, DetailView):
    pass

detail = BlogDetailView.as_view(
        model=Blog,
        context_object_name='post',
        template_name="blog/blog_details.html"
        )
