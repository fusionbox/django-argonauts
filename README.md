# django-fusionbox

Useful tools for Django development.


## `GenericTemplateFinderMiddleware`
This middleware will automagically find a template based on the request url and
render it. Useful during early design stages to allow quick static pages to use
the template system.

Add `fusionbox.middleware.GenericTemplateFinderMiddleware` to your
`MIDDLEWARE_CLASSES` to activate.

### Usage examples
- `/` renders `index.html`
- `/foo/` renders `/foo.html` OR `/foo/index.html` OR `/foo`
- This works for an directory depth


## fusionbox\_tags
Put `{% load fusionbox_tags %}` in your template to use these.

### `{% higlight_here %}`
This template tag will parse all anchor tags between `higlight_here` and
`endhighlight` and add a class to the ones that are considered 'parents' of the
current page's url. It takes an optional class name as an argument, defaulting
to `here`.


#### Usage examples

        {% highlight_here %}
            <a href="/" class="home">/</a>
            <a href="/blog/">blog</a>
        {% endhighlight %}


        {% highlight_here big red %}
            <a href="/">/</a>
            <a href="/blog/">blog</a>
        {% endhighlight %}
