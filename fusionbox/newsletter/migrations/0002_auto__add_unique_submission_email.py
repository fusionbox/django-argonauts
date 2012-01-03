# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Submission', fields ['email']
        db.create_unique('newsletter_submission', ['email'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Submission', fields ['email']
        db.delete_unique('newsletter_submission', ['email'])


    models = {
        'newsletter.submission': {
            'Meta': {'ordering': "('created_at',)", 'object_name': 'Submission'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['newsletter']
