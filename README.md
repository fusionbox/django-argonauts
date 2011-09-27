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
