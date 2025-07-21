from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import base.models 
        from . import signals

        post_save.connect(signals.db_changed, dispatch_uid="global_post_save")
        post_delete.connect(signals.db_changed, dispatch_uid="global_post_delete")
