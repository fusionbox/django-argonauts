from django.views.generic import TemplateView


class StaticServe(TemplateView):
    mimetype = 'text/html'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.mimetype)
        return super(StaticServe, self).render_to_response(context, **response_kwargs)
