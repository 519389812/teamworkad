from django.contrib import admin
from user.models import User
from django.contrib.auth.admin import UserAdmin


class NewUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'team_name', 'team_id')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'team_name', 'is_staff')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            readonly_fields = ('team_id',)
        else:
            readonly_fields = ('team_id', 'team_name')
        return readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team_id=request.user.team_id)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.team_id is None:
            obj.team_id = request.user.team_id
            obj.team_name = request.user.team_name
        if obj.team_name != request.user.team_name:
            User.objects.filter(team_id=request.user.team_id).update(team_name=obj.team_name)
        obj.save()


admin.site.register(User, NewUserAdmin)

admin.site.site_header = 'Teamwork管理系统'
admin.site.site_title = 'Teamwork管理系统'
admin.site.index_title = 'Teamwork管理系统'
