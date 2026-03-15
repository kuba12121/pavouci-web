from sqladmin import ModelView
from pavouci_api.models import Uzivatel, Pavouk, Celed, Pavucina, Nalezy

class UzivatelAdmin(ModelView, model=Uzivatel):
    column_list = [Uzivatel.id_uz, Uzivatel.jmeno, Uzivatel.email, Uzivatel.is_verified]
    name = "Uživatel"
    name_plural = "Uživatelé"
    icon = "fa-solid fa-user"

class PavoukAdmin(ModelView, model=Pavouk):
    column_list = [Pavouk.id_pavk, Pavouk.nazev, Pavouk.lat_nazev]
    name = "Pavouk"
    name_plural = "Pavouci"
    icon = "fa-solid fa-spider"

class CeledAdmin(ModelView, model=Celed):
    column_list = [Celed.id_celed, Celed.nazev]
    name = "Čeleď"
    name_plural = "Čeledi"
    icon = "fa-solid fa-layer-group"

class PavucinaAdmin(ModelView, model=Pavucina):
    column_list = [Pavucina.id_pavuc, Pavucina.typ]
    name = "Pavučina"
    name_plural = "Pavučiny"
    icon = "fa-solid fa-circle-nodes"

class NalezyAdmin(ModelView, model=Nalezy):
    column_list = [Nalezy.id_nal, Nalezy.nazev, Nalezy.lokace, Nalezy.datum]
    name = "Nález"
    name_plural = "Nálezy"
    icon = "fa-solid fa-camera"
