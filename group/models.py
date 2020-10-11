from django.db import models
from django.contrib.auth.models import Group


class NewGroup(models.Model):
    # OneToOneField的反向关联属性如果没有写relate_name, 则是对方类名的小写
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    class Meta:
        verbose_name = "授权组"
        verbose_name_plural = "授权组"

    def __str__(self):
        return self.group.name
