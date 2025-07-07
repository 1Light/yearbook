from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile, EncoderProfile

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

class EncoderProfileInline(admin.StackedInline):
    model = EncoderProfile
    can_delete = False
    verbose_name_plural = 'Encoder Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'full_name')

    # Show only relevant profile inline depending on user's role
    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:
            if obj.role == 'student':
                inline_instances = [StudentProfileInline(self.model, self.admin_site)]
            elif obj.role == 'encoder':
                inline_instances = [EncoderProfileInline(self.model, self.admin_site)]
        return inline_instances

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'role')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

admin.site.register(User, UserAdmin)
