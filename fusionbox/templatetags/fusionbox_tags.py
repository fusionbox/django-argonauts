from django import template

from BeautifulSoup import BeautifulSoup

register = template.Library()

class Highlighter(template.Node):

    @staticmethod
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

    def __init__(self, parser, token):
        self.highlight_class = ' '.join(token.split_contents()[1:])
        self.nodelist = parser.parse(('endhighlight',))
        parser.delete_first_token()


class HighlightHereNode(Highlighter):
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
    def render(self, context):
        content = self.nodelist.render(context)
        soup = BeautifulSoup(content)
        
        if not self.highlight_class:
            self.highlight_class = "here"

        for anchor in soup.findAll('a', {'href': True}):
            if self.is_here(context['request'].path, anchor['href']):
                try:
                    anchor['class'] += ' ' + self.highlight_class
                except KeyError:
                    anchor['class'] = self.highlight_class

        return str(soup)

register.tag("highlight_here", HighlightHereNode)


class HighlightHereParentNode(Highlighter):
    """
    Adds a here class to the parent of the anchor link.  Useful for nested navs where highlight
    style might bubble upwards

    Given::

    {% highlight_here %}
     <ul>
        <li id="navHome" class="parent_home">
            <a href="/" class="home">/</a>
        </li>
        <li id="navblog" class="">
            <a href="/blog/">blog</a>
        </li>
     </ul>
    {% endhighlight %}

    If request.url is ``/``, the output is::

    <ul>
        <li id="navHome" class="parent_home here">
            <a href="/" class="home">/</a>
        </li>
        <li>
            <a href="/blog/">blog</a>
        </li>
    <ul>

    """
    def render(self, context):
        content = self.nodelist.render(context)
        soup = BeautifulSoup(content)

        if not self.highlight_class:
            self.highlight_class = "here"
        for anchor in soup.findAll('a', {'href': True}):
            if self.is_here(context['request'].path, anchor['href']):
                try:
                    anchor.parent['class'] += ' ' + self.highlight_class
                except KeyError:
                    anchor.parent['class'] = self.highlight_class
        return str(soup)

register.tag("highlight_here_parent", HighlightHereParentNode)
