"""
Adapted from http://djangosnippets.org/snippets/823/
"""

import os
import pipes
from subprocess import Popen, PIPE
import time

from django.core.management.base import BaseCommand

BACKUP_DIR = 'backups'


class Command(BaseCommand):
    help = 'Backs up each database in settings.DATABASES.'
    can_import_settings = True

    class BackupError(Exception):
        pass

    def handle(self, *args, **options):
        from django.conf import settings

        current_time = time.strftime('%F-%s')

        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        # Loop through databases and backup
        for database_name in settings.DATABASES:
            config = settings.DATABASES[database_name]

            # MySQL command and args
            if config['ENGINE'] == 'django.db.backends.mysql':
                backup_cmd = self.do_mysql_backup
                backup_kwargs = {
                    'timestamp_file': os.path.join(BACKUP_DIR, '{0}-{1}.mysql.gz'.format(database_name, current_time)),
                    'db': config['NAME'],
                    'user': config['USER'],
                    'password': config.get('PASSWORD', None),
                    'host': config.get('HOST', None),
                    'port': config.get('PORT', None),
                }
            # PostgreSQL command and args
            elif config['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
                backup_cmd = self.do_postgresql_backup
                backup_kwargs = {
                    'timestamp_file': os.path.join(BACKUP_DIR, '{0}-{1}.pgsql.gz'.format(database_name, current_time)),
                    'db': config['NAME'],
                    'user': config['USER'],
                    'password': config.get('PASSWORD', None),
                    'host': config.get('HOST', None),
                    'port': config.get('PORT', None),
                }
            # SQLite command and args
            elif config['ENGINE'] == 'django.db.backends.sqlite3':
                backup_cmd = self.do_sqlite_backup
                backup_kwargs = {
                    'timestamp_file': os.path.join(BACKUP_DIR, '{0}-{1}.sqlite.gz'.format(database_name, current_time)),
                    'db_file': config['NAME'],
                }
            # Unsupported
            else:
                backup_cmd = None

            # Run backup command with args
            print '========== Backing up \'{0}\'...'.format(database_name)
            if backup_cmd:
                try:
                    backup_cmd(**backup_kwargs)
                    print '========== ...done!'
                except self.BackupError as e:
                    print e.message
                    print '========== ...skipped.'
            else:
                print 'Backup for {0} engine not implemented.'.format(config['ENGINE'])
                print '========== ...skipped.'
            print ''

    def do_mysql_backup(self, timestamp_file, db, user, password=None, host=None, port=None):
        # Build args to dump command
        dump_args = []
        dump_args += ['--user={0}'.format(pipes.quote(user))]
        if password:
            dump_args += ['--password={0}'.format(pipes.quote(password))]
        if host:
            dump_args += ['--host={0}'.format(pipes.quote(host))]
        if port:
            dump_args += ['--port={0}'.format(pipes.quote(port))]
        dump_args += [pipes.quote(db)]
        dump_args = ' '.join(dump_args)

        # Build filenames
        timestamp_file = pipes.quote(timestamp_file)

        # Build command
        cmd = 'mysqldump {dump_args} | gzip > {timestamp_file}'.format(
            dump_args=dump_args,
            timestamp_file=timestamp_file,
        )

        # Execute
        self.do_command(cmd, db)

        print 'Backed up {db}; Load with `cat {timestamp_file} | gunzip | mysql {dump_args}`'.format(
            db=db,
            timestamp_file=timestamp_file,
            dump_args=dump_args,
        )

    def do_postgresql_backup(self, timestamp_file, db, user, password=None, host=None, port=None):
        # Build args to dump command
        dump_args = []
        dump_args += ['--username={0}'.format(pipes.quote(user))]
        if password:
            dump_args += ['--password']
        if host:
            dump_args += ['--host={0}'.format(pipes.quote(host))]
        if port:
            dump_args += ['--port={0}'.format(pipes.quote(port))]
        dump_args += [pipes.quote(db)]
        dump_args = ' '.join(dump_args)

        # Build filenames
        timestamp_file = pipes.quote(timestamp_file)

        # Build command
        cmd = 'pg_dump {dump_args} | gzip > {timestamp_file}'.format(
            dump_args=dump_args,
            timestamp_file=timestamp_file,
        )

        # Execute
        self.do_command(cmd, db, password)

        print 'Backed up {db}; Load with `cat {timestamp_file} | gunzip | psql {dump_args}`'.format(
            db=db,
            timestamp_file=timestamp_file,
            dump_args=dump_args,
        )

    def do_sqlite_backup(self, timestamp_file, db_file):
        # Build filenames
        db_file = pipes.quote(db_file)
        timestamp_file = pipes.quote(timestamp_file)

        # Build command
        cmd = 'gzip < {db_file} > {timestamp_file}'.format(
            db_file=db_file,
            timestamp_file=timestamp_file,
        )

        # Execute
        self.do_command(cmd, db_file)

        print 'Backed up {db_file}; Load with `cat {timestamp_file} | gunzip > {db_file}`'.format(
            db_file=db_file,
            timestamp_file=timestamp_file,
        )

    def do_command(cls, cmd, db, password=None):
        """
        Executes a command and prints a status message.
        """
        print 'executing:'
        print cmd

        with open('/dev/null', 'w') as FNULL:
            process = Popen(cmd, stdin=PIPE, stdout=FNULL, stderr=FNULL, shell=True)

            # Enter a password through stdin if required
            if password:
                process.communicate(input='{0}\n'.format(password))
            else:
                process.wait()

            if process.returncode != 0:
                raise cls.BackupError('Error code {code} while backing up database \'{db}\'!'.format(
                    code=process.returncode,
                    db=db,
                ))
