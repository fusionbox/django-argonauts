from django.views.generic import (ListView, DetailView)

from tagging.models import Tag

from .models import *


class WithTagMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(WithTagMixin, self).get_context_data(*args, **kwargs)
        context['tags'] = Tag.objects.all()
        return context

class WithLeftNavMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(WithLeftNavMixin, self).get_context_data(*args, **kwargs)
        # lambda makes it lazy
        context['blogs_for_left_nav'] = lambda: Blog.objects.published().year_month_groups()
        context['blogs_cache_version'] = lambda: cache.get('fusionbox.blog.all_blogs.version')
        return context


class IndexView(WithTagMixin, WithLeftNavMixin, ListView):
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
            context['tag'] = Tag.objects.get(name=self.kwargs['tag'])
        except:
            pass
        try:
            context['author'] = User.objects.get(id=self.kwargs['author_id'])
        except:
            pass
        return context

index = IndexView.as_view(template_name="blog/blog_list.html")


class TagDetailView(WithTagMixin, WithLeftNavMixin, DetailView):
    pass

detail = TagDetailView.as_view(
        model=Blog,
        context_object_name='post',
        template_name="blog/blog_details.html"
        )
