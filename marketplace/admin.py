from django.contrib import admin

from .models import Application, Category, Project


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    ordering = ["name"]
    date_hierarchy = "created_at"
    prepopulated_fields = {}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "client", "category", "budget", "status", "created_at"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "description", "client__username"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Project Information", {"fields": ("title", "description", "category")}),
        ("Budget & Timeline", {"fields": ("budget", "deadline")}),
        ("Assignment", {"fields": ("client", "assigned_freelancer", "status")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("client", "category", "assigned_freelancer")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "freelancer",
        "status",
        "proposed_timeline",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["project__title", "freelancer__username", "cover_letter"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Application Details", {"fields": ("project", "freelancer", "status")}),
        (
            "Proposal",
            {"fields": ("cover_letter", "proposed_timeline", "proposed_budget")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("project", "freelancer")
