from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, Skill, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_staff", "created_at"]
    list_filter = ["role", "is_staff", "is_superuser", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = BaseUserAdmin.fieldsets + (("Additional Info", {"fields": ("role",)}),)

    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Additional Info", {"fields": ("role",)}),)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    ordering = ["name"]
    date_hierarchy = "created_at"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "hourly_rate", "created_at"]
    list_filter = ["created_at", "skills"]
    search_fields = ["user__username", "user__email", "bio"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    filter_horizontal = ["skills"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        ("Profile Details", {"fields": ("bio", "hourly_rate", "avatar", "skills")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
