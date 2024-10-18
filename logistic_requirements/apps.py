# logistic_requirements/apps.py
from django.apps import AppConfig

class LogisticRequirementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logistic_requirements'

    def ready(self):
        # Importa las señales para asegurarte de que se registren al iniciar la aplicación
        import logistic_requirements.signals
