# See LICENSE file for copyright and license details.
"""
Budget app config.
"""
from django.apps import AppConfig


class BudgetConfig(AppConfig):
    """
    Buged app config.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget'
