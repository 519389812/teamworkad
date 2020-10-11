from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=150, verbose_name="名")
    last_name = models.CharField(max_length=150, verbose_name="姓")
    full_name = models.CharField(max_length=16, verbose_name="全名")
    team_name = models.TextField(max_length=50, verbose_name="团队名称")
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.full_name = self.last_name + self.first_name
        super(User, self).save(*args, **kwargs)
