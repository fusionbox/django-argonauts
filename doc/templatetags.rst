Template Tags
=============

The :mod:`fusionbox_tags` library contains several useful template tags. Use
``{% load fusionbox_tags %}`` to use these.


``highlight_here``
------------------

Filter the subnode's output to add a class to every anchor where
appropriate, based on startswith matching. By default the class is ``here``,
but you can override by passing an argument to the tag.

.. note::
    This requires BeautifulSoup to do the HTML parsing

Examples
--------
.. highlight:: html

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



Code
----

.. automodule:: fusionbox.core.templatetags.fusionbox_tags
    :members:
