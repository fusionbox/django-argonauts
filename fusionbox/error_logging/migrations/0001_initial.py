# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Logged404'
        db.create_table('error_logging_logged404', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 8, 17, 0, 0))),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('referer', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('is_internal', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('error_logging', ['Logged404'])

        # Adding unique constraint on 'Logged404', fields ['domain', 'referer', 'path', 'is_internal']
        db.create_unique('error_logging_logged404', ['domain', 'referer', 'path', 'is_internal'])


    def backwards(self, orm):
        # Removing unique constraint on 'Logged404', fields ['domain', 'referer', 'path', 'is_internal']
        db.delete_unique('error_logging_logged404', ['domain', 'referer', 'path', 'is_internal'])

        # Deleting model 'Logged404'
        db.delete_table('error_logging_logged404')


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