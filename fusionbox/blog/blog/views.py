from django.views.generic import *

from tagging.models import Tag

from .models import *


class WithTagMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(WithTagMixin, self).get_context_data(*args, **kwargs)
        context['tags'] = Tag.objects.all()
        return context

class IndexView(WithTagMixin, ListView):
    model=Blog
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = Blog.published.order_by('-created_at')
        try:
            return self.model.tagged.with_all([self.kwargs['tag']], qs)
        except KeyError:
            return qs

index = IndexView.as_view()

class TagDetailView(WithTagMixin, DetailView):
    pass

detail = TagDetailView.as_view(
        model=Blog,
        context_object_name = 'post',
        )
