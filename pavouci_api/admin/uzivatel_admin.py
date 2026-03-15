from sqladmin import ModelView
from pavouci_api.models import Uzivatel

class UzivatelAdmin(ModelView, model=Uzivatel):
    column_list = [Uzivatel.ID_uz, Uzivatel.Jmeno, Uzivatel.Email]
    name = "Uživatel"
    name_plural = "Uživatelé"
