from django.apps import AppConfig
import logging


class CatalogConfig(AppConfig):
    name = 'catalog'

    def ready(self):
        from .prjconfig import Configuration
        c = Configuration.get_object() 
        logging.info("App ready: catalog")
