from django.contrib import admin
from team.models import Team
from user.models import User


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "get_member", )
    list_display_links = ("name", )
    search_fields = ("name", )
    filter_horizontal = ("member", )
    fields = ("name", "member", )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team_id=request.user.team_id)

    def get_member(self, obj):
        return ' '.join([i.full_name for i in obj.member.all()])

    get_member.short_description = "成员"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.team_id is None:
            obj.team_id = request.user.team_id
        obj.save()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "member":
            # 过滤
            kwargs["queryset"] = User.objects.filter(team_id=request.user.team_id)
            # filter_horizontal 保持横向展示
            from django.contrib.admin import widgets
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(TeamAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Team, TeamAdmin)
