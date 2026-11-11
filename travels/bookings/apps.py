from django.apps import AppConfig


class Bookingsconfig(AppConfig):
    default_auto_field="django.db.models.BigAutoField"
    name = "bookings"

    def ready(Self):
     
       import bookings.signals