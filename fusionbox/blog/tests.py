import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from fusionbox.blog.models import Blog

class BlogTest(TestCase):
    def test_year_month_groups(self):
        author = User.objects.create()
        a = Blog.objects.create(
                created_at=datetime.date(2011, 12, 12),
                publish_at=datetime.date(2011, 12, 12),
                is_published=True,
                author=author,
                )
        b = Blog.objects.create(
                created_at=datetime.date(2012, 10, 10),
                publish_at=datetime.date(2011, 12, 12),
                is_published=True,
                author=author,
                )

        groups = Blog.objects.year_month_groups()
        assert len(groups) == 2 # 2 years
        assert len(groups[2011]) == 1
        assert len(groups[2012]) == 1
        assert groups[2011][12][0] == a
        assert groups[2012][10][0] == b
