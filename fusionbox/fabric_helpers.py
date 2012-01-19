from contextlib import contextmanager as _contextmanager

from fabric.api import *
from fabric.contrib.console import *


@_contextmanager
def virtualenv(dir):
    with prefix('source %s/bin/activate' % dir):
        yield

def files_changed(version, files):
    """
    Between version and HEAD, has anything in files changed?
    """
    if not isinstance(files, basestring):
        files = ' '.join(files)
    return "diff" in local("git diff %s HEAD -- %s" % (version, files), capture=True)

def get_git_branch():
    return local("git branch --no-color 2> /dev/null|grep '^*'|sed 's/^* //'", capture=True)

def is_repo_clean():
    with settings(warn_only=True):
        return run("git status 2>&1|grep 'nothing to commit' > /dev/null").succeeded

def update_git(branch):
    """
    Updates the remote git repo to ``branch``
    """
    # Use a bundle because fabric won't forward agent
    if not is_repo_clean():
        if not confirm("Remote repo is not clean, stash and continue?"):
            abort("Remote repo dirty, aborting")
        run("git stash")
    run("git checkout '%s'" % branch)
    remote_head = run("git rev-parse HEAD")
    with settings(warn_only=True):
        if local("git bundle create .git/deploy_bundle '%s'..'%s'" % (remote_head, branch)).return_code == 128:
            puts("already up to date")
            return remote_head
    put(".git/deploy_bundle", ".git/deploy_bundle")
    run("git pull .git/deploy_bundle %s" % branch)
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
        version = update_git(branch or get_git_branch())
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
