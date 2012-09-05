# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        if settings.DATABASES['default']['engine'] == 'django.db.backends.postgresql_psycopg2':
            db.create_index('error_logging_logged404', ['domain', 'referer', 'path', 'is_internal'], unique=True)

    def backwards(self, orm):
        if settings.DATABASES['default']['engine'] == 'django.db.backends.postgresql_psycopg2':
            db.delete_index('error_logging_logged404', ['domain', 'referer', 'path', 'is_internal'])

    models = {
        'error_logging.logged404': {
            'Meta': {'ordering': "('-created_at',)", 'unique_together': "(('domain', 'referer', 'path', 'is_internal'),)", 'object_name': 'Logged404'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 17, 0, 0)'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_internal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'referer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['error_logging']
