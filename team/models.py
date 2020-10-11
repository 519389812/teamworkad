from django.db import models
from user.models import User


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True, verbose_name="组名")
    member = models.ManyToManyField(User, related_name="member", default=None, blank=True, verbose_name="成员")
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    class Meta:
        verbose_name = "分组"
        verbose_name_plural = "分组"

    def __str__(self):
        return self.name
