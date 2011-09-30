from django import template

from BeautifulSoup import BeautifulSoup

register = template.Library()

def is_here(current, url):
    """
    Determine if current is 'underneath' url.
    """
    if url == '/':
        return current == '/'
    if current.startswith(url):
        return True
    else:
        return False

class HighlightHereNode(template.Node):
    """
    Filter the subnode's output to add a 'here' class to every anchor where
    appropriate, based on startswith matching.

    Given::

        {% highlight_here %}
            <a href="/" class="home">/</a>
            <a href="/blog/">blog</a>
        {% endhighlight %}

    If request.url is ``/``, the output is::

        <a href="/" class="home here">/</a>
        <a href="/blog/">blog</a>

    On ``/blog/``, it is::

        <a href="/" class="home">/</a>
        <a href="/blog/" class="here">blog</a>

    """
    def __init__(self, parser, token):
        self.here_class = ' '.join(token.split_contents()[1:])
        if not self.here_class:
            self.here_class = 'here'
        self.nodelist = parser.parse(('endhighlight',))
        parser.delete_first_token()

    def render(self, context):
        content = self.nodelist.render(context)
        soup = BeautifulSoup(content)

        for anchor in soup.findAll('a', {'href': True}):
            if is_here(context['request'].path, anchor['href']):
                try:
                    anchor['class'] += ' ' + self.here_class
                except KeyError:
                    anchor['class'] = self.here_class

        return str(soup)

register.tag('highlight_here', HighlightHereNode)
