from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from group.models import NewGroup


class NewGroupInline(admin.StackedInline):
    model = NewGroup
    can_delete = False
    verbose_name_plural = '授权组'
    readonly_fields = ("team_id", )


class NewGroupAdmin(GroupAdmin):
    inlines = (NewGroupInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        group = Group.objects.get(name=obj.name)
        # 检查若object无onetoonefield的属性，则表示未创建，则创建
        if not hasattr(group, "newgroup"):
            NewGroup.objects.create(group=group, team_id=request.user.team_id)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # filter表示以newgroup表中的team_id field来筛选
        return qs.filter(newgroup__team_id=request.user.team_id)


admin.site.unregister(Group)
admin.site.register(Group, NewGroupAdmin)
