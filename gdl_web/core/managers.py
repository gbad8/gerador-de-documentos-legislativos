from django.db import models


class TenantManager(models.Manager):
    def for_camara(self, camara):
        return self.filter(camara=camara)
