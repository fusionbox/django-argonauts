from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .forms import UserForm

def content(request):
    current = []
    env = {}

    if request.user.is_authenticated():
        for field in User._meta.fields:
            if field.name == 'password':
                continue
            current.append(
                (field.attname, getattr(request.user, field.attname))
            )

    if 'primary_user' in request.session:
        env['display'] = True
        env['primary'] = User.objects.get(pk=request.session['primary_user'])
        env['form'] = UserForm()
        env['next'] = request.GET.get('next')
        env['users'] = User.objects.order_by('-last_login')[:10]
        env['current'] = current
    else:
        env['display'] = False


    return render_to_response('debug_toolbar_user_panel/content.html', env, context_instance=RequestContext(request))

@csrf_exempt
@require_POST
def login_form(request):
    if not 'primary_user' in request.session:
        raise PermissionDenied
    form = UserForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest()

    return login(request, **form.get_lookup())

@csrf_exempt
@require_POST
def login(request, **kwargs):
    if not 'primary_user' in request.session:
        raise PermissionDenied
    primary = get_object_or_404(User, pk=request.session['primary_user'])
    user = get_object_or_404(User, **kwargs)

    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    auth.login(request, user)

    request.session['primary_user'] = primary.id

    return HttpResponseRedirect(request.POST.get('next', '/'))
