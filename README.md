# django-fusionbox

Useful tools for Django development.


## `GenericTemplateFinderMiddleware` This middleware will automatically find a
template based on the request url and render it. Useful during early design
stages to allow quick static pages to use the template system.

Add `fusionbox.middleware.GenericTemplateFinderMiddleware` to your
`MIDDLEWARE_CLASSES` to activate.

### Usage examples
- `/` renders `index.html`
- `/foo/` renders `/foo.html` OR `/foo/index.html` OR `/foo`
- This works for any directory depth

## `RedirectFallbackMiddleware` Middleware for handling 3xx redirects and 410
pages.  Scrapes `/redirects/` in your project, or a path defined in
`settings.REDIRECTS_DIRECTORY` for any CSV files.  CSV files should be in the
format of `old_url, new_url, status_code`.  If `status_code` is omitted, a 301
will be issued.  If both `new_url` and `status_code` are omitted, a 410 will be
issued.  Both url fields can be either relative or fully qualified urls.
Redirects will only be issued for pages which would normally result in a 404.

Errors are raised when any url produces a redirect chain.  Since fully
qualified urls are accepted, warnings are raised in the event that a redirect
could produce a circular redirect dependent on the site's domain.

This middleware should be placed before django's built in 'CommonMiddleware'.

Add `fusionbox.middleware.RedirectFallbackMiddleware` to your
`MIDDLEWARE_CLASSES` to activate.  Run `./manage.py validate_redirects` to
check redirects for problem and view any warnings raised.

### Example Valid CSV http://www.fusionbox.com/foo/, /bar/
http://www.fusionbox.com/baz/, /asdf/, 302 /fdsa/,
http://www.fusionbox.com/asdf/ /something/, http://www.google.com/
/another-thing/

### Example CSV with circular redirects or error redirects
http://www.fusionbox.com/foo/, /bar/ http://www.fusionbox.com/bar/, /baz/

    http://www.fusionbox.com/bar/, /bar/

### Example CSV with redirects which raise warnings.  /foo/,
http://www.fusionbox.com/foo/

## Behaviors Behaviors are a [DRY](http://c2.com/cgi/wiki?DontRepeatYourself)
way of re-using common fields and methods on models. Behaviors function
seamlessly through python inheritance and are fully configurable. Behaviors
also support multi-inheritance so adding multiple behaviors to a single model
is as easy as inheriting from each behavior you wish to add.

### Standard Usage from fusionbox.behaviors import TimeStampable

    class Foo(TimeStampable): pass

This will add the fields `created_at` and `updated_at` to your `Foo` model.

Just as their names suggest, the model will have the following fields.

* `created_at` => `DateTimeField(auto_now_add=True)`
* `updated_at` => `DateTimeField(auto_now=True)`

### Custom Configuration Usage from fusionbox.behaviors import TimeStampable

    class Foo(TimeStampable): class TimeStampable: created_at = "creation_date"
    updated_at = "date_updated"

This will add the same fields as in the standard usage, but the fields will
instead be named `creation_date` and `date_updated` respectively

## fusionbox\_tags Put `{% load fusionbox_tags %}` in your template to use
these.

### `{% higlight_here %}` This template tag will parse all anchor tags between
`higlight_here` and `endhighlight` and add a class to the ones that are
considered 'parents' of the current page's url. It takes an optional class name
as an argument, defaulting to `here`.


#### Usage examples

        {% highlight_here %} <a href="/" class="home">/</a> <a
        href="/blog/">blog</a> {% endhighlight %}


        {% highlight_here big red %} <a href="/">/</a> <a
        href="/blog/">blog</a> {% endhighlight %}

## Decorators

`require_PUT`, `require_DELETE` - just like the built-in `require_POST` and
`require_GET` decorators.

`require_AJAX` - uses django's `request.is_ajax()` method, returns
`HttpResponseBadRequest` if the request is not an AJAX request.

    @require_AJAX def my_view(request): pass

`require_JSON` - makes sure that the `Content-Type` header is
`application/json`, and parses the JSON if it is.  Assigns the result to
`request.payload`.  If an error occurs, an `HttpResponseBadRequest` is
returned.

    @require_JSON def my_view(request): print request.payload

## Forms

###`fusionbox.forms.SearchForm`

Mixin form class which provides a searching interface on a model

###`fusionbox.forms.SortForm`

Mixin form class which provides singular and progressive sorting on a model
along with headers for use in template rendering.

###`fusionbox.forms.FilterForm`

Mixin form class which provides a filtering interface on a model
