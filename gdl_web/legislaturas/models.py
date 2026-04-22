from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.managers import TenantManager
from core.models import Camara


class Legislatura(models.Model):
    numero = models.PositiveIntegerField("Número")
    data_eleicao = models.DateField("Data da Eleição")
    data_inicio = models.DateField("Data de Início")
    data_fim = models.DateField("Data de Fim")
    
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)

    objects = TenantManager()

    class Meta:
        verbose_name_plural = "Legislaturas"
        ordering = ["-numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["camara", "numero"],
                name="unique_legislatura_por_camara"
            )
        ]
        indexes = [
            models.Index(fields=["camara"]),
        ]

    def __str__(self):
        return f"{self.numero}ª Legislatura"

    def clean(self):
        super().clean()
        
        # Validates that data_inicio is before data_fim
        if self.data_inicio and self.data_fim and self.data_inicio > self.data_fim:
            raise ValidationError({
                "data_inicio": "A data de início não pode ser posterior à data de fim.",
                "data_fim": "A data de fim não pode ser anterior à data de início."
            })
        
        # Date overlap validation
        camara_id = getattr(self, 'camara_id', None)
        if camara_id and self.data_inicio and self.data_fim:
            overlapping = Legislatura.objects.filter(
                camara_id=camara_id,
            ).filter(
                Q(data_inicio__lte=self.data_fim, data_fim__gte=self.data_inicio)
            )
            
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
                
            if overlapping.exists():
                raise ValidationError(
                    "O período desta legislatura se sobrepõe ao período de "
                    "outra legislatura já cadastrada."
                )
