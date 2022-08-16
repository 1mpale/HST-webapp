from django.apps import AppConfig
import pickle



class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages"
    HST = pickle.load(open('HST_full.sav', 'rb'))
    

    