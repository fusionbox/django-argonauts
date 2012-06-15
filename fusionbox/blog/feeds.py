from django.core import urlresolvers
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.http import Http404

from tagging.models import Tag, TaggedItem

from fusionbox.blog.models import Blog

class BlogFeed(Feed):
    title = "Blog"
    link = urlresolvers.reverse_lazy('blog:blog_index')

    def items(self, obj):
        if isinstance(obj, User):
            return obj.blogs.all()
        elif isinstance(obj, Tag):
            return TaggedItem.objects.get_by_model(Blog, obj)
        else:
            return Blog.objects.all()

    def item_description(self, item):
        return item.body

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.first_name + item.author.last_name

    def item_author_link(self, item):
        return urlresolvers.reverse('blog:author', kwargs={'author_id': item.author.id})

    def item_author_email(self, item):
        return item.author.email

    def item_pubdate(self, item):
        return item.publish_at

    def item_categories(self, item):
        return [i.name for i in Tag.objects.get_for_object(item)]

    def get_object(self, request, *args, **kwargs):
        try:
            return User.objects.get(id=kwargs['author_id'])
        except User.DoesNotExist:
            raise Http404
        except KeyError:
            pass

        try:
            return Tag.objects.get(name=kwargs['tag'])
        except Tag.DoesNotExist:
            raise Http404
        except KeyError:
            pass

