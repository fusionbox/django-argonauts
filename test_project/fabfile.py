from fusionbox.fabric_helpers import *

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        }

env.project_name = 'test_project'
env.short_name = 'test_project'

stage = roles('dev')(stage)
