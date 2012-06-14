import tempfile
import shutil
from StringIO import StringIO

from contextlib import contextmanager as _contextmanager

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.project import rsync_project


@_contextmanager
def virtualenv(dir):
    with prefix('source %s/bin/activate' % dir):
        yield


def files_changed(version, files):
    """
    Between version and HEAD, has anything in files changed?
    """
    if not version:
        return True
    if not isinstance(files, basestring):
        files = ' '.join(files)
    return "diff" in local("git diff %s HEAD -- %s" % (version, files), capture=True)


def update_git(branch):
    """
    Updates the remote git repo to ``branch``. Returns the previous remote git
    version.
    """
    with settings(warn_only=True):
        remote_head = run("cat static/.git_version.txt")
        if remote_head.failed:
            remote_head = None
    try:
        loc = tempfile.mkdtemp()
        put(StringIO(local('git rev-parse %s' % branch, capture=True) + "\n"), 'static/.git_version.txt', mode=0775)
        local("git archive %s | tar xf - -C %s" % (branch, loc))
        local("chmod g+rwX -R %s" % (loc)) # force group permissions
        # env.cwd is documented as private, but I'm not sure how else to do this
        with settings(warn_only=True):
            loc = loc + '/' # without this, the temp directory will get uploaded instead of just its contents
            rsync_project(env.cwd, loc, extra_opts='--chmod=g=rwX,a+rX')
    finally:
        shutil.rmtree(loc)
    return remote_head


env.tld = '.com'
def stage(pip=False, migrate=False, syncdb=False, branch=None):
    """
    stage will update the remote git version to your local HEAD, collectstatic, migrate and
    update pip if necessary.

    Set ``env.project_name`` and ``env.short_name`` appropriately to use.
    ``env.tld`` defaults to ``.com``
    """
    with cd('/var/www/%s%s' % (env.project_name, env.tld)):
        version = update_git(branch or 'HEAD')
        update_pip = pip or files_changed(version, "requirements.txt")
        migrate = migrate or files_changed(version, "*/migrations/* %s/settings.py requirements.txt" % env.project_name)
        syncdb = syncdb or files_changed(version, "*/settings.py")
        with virtualenv('/var/python-environments/%s' % env.short_name):
            if update_pip:
                run("pip install -r ./requirements.txt")
            if syncdb:
                run("./manage.py syncdb")
            if migrate:
                run("./manage.py backupdb")
                run("./manage.py migrate")
            run("./manage.py collectstatic --noinput")
        run("sudo touch /etc/vassals/%s.ini" % env.short_name)

def deploy():
    """
    Like stage, but always migrates, pips, and uses the live branch
    """
    stage(True, True, True, "live")
