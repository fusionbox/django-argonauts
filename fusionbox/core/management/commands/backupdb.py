"""
Adapted from http://djangosnippets.org/snippets/823/
"""

import os, time, pipes, popen2
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
            outfile = os.path.join(backup_dir, '%s-%s.sql.gz' % (database_name, time.strftime('%F-%s')))
            if config['ENGINE'] == 'django.db.backends.mysql':
                self.do_mysql_backup(outfile,
                                     config['NAME'],
                                     config['USER'],
                                     config.get('PASSWORD', None),
                                     config.get('HOST', None),
                                     config.get('PORT', None))
            elif config['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
                self.do_postgresql_backup(outfile,
                                     config['NAME'],
                                     config['USER'],
                                     config.get('PASSWORD', None),
                                     config.get('HOST', None),
                                     config.get('PORT', None))
            else:
                print 'Backup in %s engine not implemented' % config['ENGINE']


    def do_mysql_backup(self, outfile, db, user, password=None, host=None, port=None):
        args = []
        if user:
            args += ["--user=%s" % pipes.quote(user)]
        if password:
            args += ["--password=%s" % pipes.quote(password)]
        if host:
            args += ["--host=%s" % pipes.quote(host)]
        if port:
            args += ["--port=%s" % pipes.quote(port)]
        args += [pipes.quote(db)]

        c = 'mysqldump %s | gzip > %s' % (' '.join(args), outfile)
        print c
        os.system(c)
        print "Backed up %s; Load with `cat %s | gunzip | mysql %s`" % (db, pipes.quote(outfile), ' '.join(args))


    def do_postgresql_backup(self, outfile, db, user, password=None, host=None, port=None):
        args = []
        if user:
            args += ["--username=%s" % user]
        if password:
            args += ["--password"]
        if host:
            args += ["--host=%s" % host]
        if port:
            args += ["--port=%s" % port]
        if db:
            args += [db]
        c = 'pg_dump %s | gzip > %s' % (' '.join(args), outfile)
        print c
        pipe = popen2.Popen4(c)
        if password:
            pipe.tochild.write('%s\n' % password)
            pipe.tochild.close()
        retcode = pipe.wait()
        assert retcode == 0
        print "Backed up %s; Load with `cat %s | gunzip | psql %s`" % (db, pipes.quote(outfile), ' '.join(args))
