"""
Adapted from http://djangosnippets.org/snippets/823/
"""
import glob
import os
import pipes
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand, CommandError

from .backupdb import BACKUP_DIR


def get_latest_file(pattern):
    l = glob.glob(pattern)
    l.sort()
    l.reverse()
    return l[0] if l else None


def require_latest_exists(func):
    def new_func(self, **kwargs):
        latest_file = kwargs['latest_file']
        if not os.path.exists(latest_file):
            raise Command.RestoreError(
                'Could not find file \'{0}\'!'.format(latest_file)
            )
        else:
            return func(self, **kwargs)
    return new_func


def require_root_user(func):
    def new_func(self, **kwargs):
        if not kwargs.get('root_user', None):
            raise Command.RestoreError(
                'Please specify a ROOT_USER and ROOT_PASSWORD in the database configuration.'
            )
        else:
            return func(self, **kwargs)
    return new_func


class Command(BaseCommand):
    help = 'Restores each database in settings.DATABASES from latest db backup.'
    can_import_settings = True

    class RestoreError(Exception):
        pass

    def handle(self, *args, **options):
        from django.conf import settings

        if not os.path.exists(BACKUP_DIR):
            raise CommandError('Backup dir \'{0}\' does not exist!'.format(BACKUP_DIR))

        # Loop through databases and restore
        for database_name in settings.DATABASES:
            config = settings.DATABASES[database_name]

            # MySQL command and args
            if config['ENGINE'] == 'django.db.backends.mysql':
                restore_cmd = self.do_mysql_restore
                latest_file = get_latest_file('{0}/*.mysql.gz'.format(BACKUP_DIR))
                if not latest_file:
                    raise CommandError('No MySQL backups found!')
                restore_kwargs = {
                    'latest_file': latest_file,
                    'db': config['NAME'],
                    'user': config.get('USER', None),
                    'password': config.get('PASSWORD', None),
                    'host': config.get('HOST', None),
                    'port': config.get('PORT', None),
                }
            # PostgreSQL command and args
            elif config['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
                restore_cmd = self.do_postgresql_restore
                latest_file = get_latest_file('{0}/*.pgsql.gz'.format(BACKUP_DIR))
                if not latest_file:
                    raise CommandError('No PostgreSQL backups found!')
                restore_kwargs = {
                    'latest_file': latest_file,
                    'db': config['NAME'],
                    'user': config.get('USER', None),
                    'root_user': config.get('ROOT_USER', None),
                    'root_password': config.get('ROOT_PASSWORD', None),
                    'host': config.get('HOST', None),
                    'port': config.get('PORT', None),
                }
            # SQLite command and args
            elif config['ENGINE'] == 'django.db.backends.sqlite3':
                restore_cmd = self.do_sqlite_restore
                latest_file = get_latest_file('{0}/*.sqlite.gz'.format(BACKUP_DIR))
                if not latest_file:
                    raise CommandError('No SQLite backups found!')
                restore_kwargs = {
                    'latest_file': latest_file,
                    'db_file': config['NAME'],
                }
            # Unsupported
            else:
                restore_cmd = None

            # Run restore command with args
            print '========== Restoring \'{0}\'...'.format(database_name)
            if restore_cmd:
                try:
                    restore_cmd(**restore_kwargs)
                    print '========== ...done!'
                except self.RestoreError as e:
                    print e.message
                    print '========== ...skipped.'
            else:
                print 'Restore for {0} engine not implemented.'.format(config['ENGINE'])
                print '========== ...skipped.'
            print ''

    @require_latest_exists
    def do_mysql_restore(self, latest_file, db, user, password=None, host=None, port=None):
        # Build args to restore command
        restore_args = []
        restore_args += ['--user={0}'.format(pipes.quote(user))]
        if password:
            restore_args += ['--password={0}'.format(pipes.quote(password))]
        if host:
            restore_args += ['--host={0}'.format(pipes.quote(host))]
        if port:
            restore_args += ['--port={0}'.format(pipes.quote(port))]
        restore_args += [pipes.quote(db)]
        restore_args = ' '.join(restore_args)

        # Sanitize other args
        latest_file = pipes.quote(latest_file)

        # Build commands
        drop_cmd = 'mysqldump {restore_args} --no-data | grep "^DROP" | mysql {restore_args}'.format(
            restore_args=restore_args,
        )
        restore_cmd = 'cat {latest_file} | gunzip | mysql {restore_args}'.format(
            drop_cmd=drop_cmd,
            latest_file=latest_file,
            restore_args=restore_args,
        )

        # Execute
        self.do_command(drop_cmd, 'clearing', db)
        self.do_command(restore_cmd, 'restoring', db)

    @require_latest_exists
    @require_root_user
    def do_postgresql_restore(self, latest_file, db, user, root_user=None, root_password=None, host=None, port=None):
        # Build args to restore command
        restore_args = []
        restore_args += ['--username={0}'.format(pipes.quote(root_user))]
        if root_password:
            restore_args += ['--password']
        if host:
            restore_args += ['--host={0}'.format(pipes.quote(host))]
        if port:
            restore_args += ['--port={0}'.format(pipes.quote(port))]
        restore_args += [pipes.quote(db)]
        restore_args = ' '.join(restore_args)

        # Sanitize other args
        user = pipes.quote(user)
        latest_file = pipes.quote(latest_file)

        # Build commands
        drop_cmd = 'dropdb {restore_args}'.format(restore_args=restore_args)
        create_cmd = 'createdb {restore_args} --owner={user}'.format(
            restore_args=restore_args,
            user=user,
        )
        restore_cmd = 'cat {latest_file} | gunzip | psql {restore_args}'.format(
            latest_file=latest_file,
            restore_args=restore_args,
        )

        # Execute
        self.do_command(drop_cmd, 'dropping', db, root_password)
        self.do_command(create_cmd, 'creating', db, root_password)
        self.do_command(restore_cmd, 'restoring', db, root_password)

    @require_latest_exists
    def do_sqlite_restore(self, latest_file, db_file):
        # Build filenames
        db_file = pipes.quote(db_file)
        latest_file = pipes.quote(latest_file)

        # Build command
        cmd = 'cat {latest_file} | gunzip > {db_file}'.format(
            latest_file=latest_file,
            db_file=db_file,
        )

        # Execute
        self.do_command(cmd, 'restoring', db_file)

    def do_command(cls, cmd, verb, db, password=None):
        """
        Executes a command and prints a status message.
        """
        print '{0} database...executing:'.format(verb.capitalize())
        print cmd

        with open('/dev/null', 'w') as FNULL:
            process = Popen(cmd, stdin=PIPE, stdout=FNULL, stderr=FNULL, shell=True)

            # Enter a password through stdin if required
            if password:
                process.communicate(input='{0}\n'.format(password))
            else:
                process.wait()

            if process.returncode != 0:
                raise cls.RestoreError('Error code {code} while {verb} database \'{db}\'!'.format(
                    code=process.returncode,
                    verb=verb,
                    db=db,
                ))
