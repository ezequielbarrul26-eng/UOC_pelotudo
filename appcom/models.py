from django.db import models
from django.conf import settings


class Perfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )
    direccion = models.CharField(
        max_length=255,
        blank=True
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Partida(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="partidas_blackjack"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    apuesta = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    puntos = models.IntegerField(default=0)
    resultado = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return f"Partida {self.id} - {self.usuario}"