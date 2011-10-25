"""
Adapted from http://djangosnippets.org/snippets/823/
"""

import os, time, pipes
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Backs up each database in settings.DATABASES."
    can_import_settings = True
    def handle(self, *args, **options):
        from django.conf import settings

        backup_dir = 'tmp'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        for database_name in settings.DATABASES:
            config = settings.DATABASES[database_name]
            if config['ENGINE'] != 'django.db.backends.mysql':
                print 'Backup in %s engine not implemented' % self.engine
            outfile = os.path.join(backup_dir, '%s-%s.sql.gz' % (database_name, time.strftime('%F-%s')))
            self.do_mysql_backup(outfile,
                                 config['NAME'],
                                 config['USER'],
                                 config.get('PASSWORD', None),
                                 config.get('HOST', None),
                                 config.get('PORT', None))

    def do_mysql_backup(self, outfile, db, user, password=None, host=None, port=None):
        args = []
        if user:
            args += ["--user=%s" % pipes.quote(user)]
        if password:
            args += ["--password=%s" % pipes.quote(passwd)]
        if host:
            args += ["--host=%s" % pipes.quote(host)]
        if port:
            args += ["--port=%s" % pipes.quote(port)]
        args += [pipes.quote(db)]

        c = 'mysqldump %s | gzip > %s' % (' '.join(args), outfile)
        print c
        os.system(c)
        print "Backed up %s; Load with `cat %s | gunzip > mysql %s`" % (db, pipes.quote(outfile), ' '.join(args))
