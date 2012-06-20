import random
import datetime
import urllib
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import File

from fusionbox.blog.models import Blog

word_list = ['john', 'intense', 'lucky', 'solid', 'hot', 'clever', 'amusing', 'wicked', 'damp', 'sticky', 'warm', 'courteous', 'young', 'slow', 'selfish', 'great', 'vigorous', 'glamorous', 'clean', 'placid', 'enthusiastic', 'instinctive', 'wild', 'hurt', 'tricky', 'diplomatic', 'sympathetic', 'painstaking', 'raspy', 'proud', 'thoughtful', 'delicious', 'itchy', 'cute', 'debtor', 'trip', 'france', 'cone', 'missile', 'statistic', 'equipment', 'push', 'fine', 'antarctica', 'apparel', 'meteorology', 'tsunami', 'head', 'balance', 'fowl', 'spoon', 'croissant', 'library', 'purchase', 'staircase', 'wasp', 'carnation', 'cannon', 'bronze', 'glass', 'kendo', 'cello', 'taiwan', 'shape', 'cauliflower', 'green', 'run', 'scarf', 'tower', 'regret', 'disgust', 'roof', 'hen', 'law',]

tags = ['broccoli', 'violin', 'disintermediate', 'infomediaries', '"compelling synergy"']

names = ['John', 'Patrick', 'Alberto', 'Bertha', 'Claudette', 'Arlene', 'Vince']

def random_text(nwords, choices=word_list):
    words = []
    got_words = 0
    while got_words < nwords:
        word = random.choice(choices)
        if got_words % 10 == 0 and got_words != 0:
            word += '.'
        if got_words % 50 == 0 and got_words != 0:
            words += '\n\n\n'
        words.append(word)
        got_words += 1
    return ' '.join(words)

def random_image(word='unicorn'):
    tmpfile, header = urllib.urlretrieve('http://placenoun.com/' + urllib.quote_plus(word))
    name = random_text(3)
    return default_storage.save(name, File(open(tmpfile), name=name))

class Command(BaseCommand):
    help = "Creates some random blogs"
    option_list = BaseCommand.option_list + (
    make_option('--images',
        action='store_true',
        default=False,
        help='Include some random images'),
    )
    def handle(self, *args, **options):
        author = User.objects.create(
                first_name=random_text(1, names),
                last_name=random_text(1, names),
                username=random_text(3).replace(' ', ''),
                email="%s@%s.com" % (random_text(2), random_text(1)),
                )

        for i in range(25):
            body = random_text(500)
            title_first = random_text(1)
            Blog.objects.create(
                    title=title_first + ' ' + random_text(4),
                    author=author,
                    summary=body[:40],
                    body=body,
                    tags=random_text(2, tags),
                    is_published=True,
                    publish_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 1000)),
                    created_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 1000)),
                    image=random_image(title_first) if options['images'] and random.randint(0,3)==0 else None,
                    )
