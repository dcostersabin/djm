from django.apps import apps
from django.contrib import admin

app_config = apps.get_app_config("djm")
for model_name, model in app_config.models.items():
    if not admin.site.is_registered(model):
        admin.site.register(model)
