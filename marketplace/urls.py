from django.urls import path

from . import views

app_name = "marketplace"

urlpatterns = [
    # Project URLs
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("project/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("project/create/", views.project_create, name="project_create"),
    path("project/<int:pk>/update/", views.project_update, name="project_update"),
    path("project/<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("project/<int:pk>/complete/", views.project_complete, name="project_complete"),
    # Category URLs
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("category/<int:pk>/", views.CategoryDetailView.as_view(), name="category_detail"),
    # Application URLs
    path(
        "project/<int:project_pk>/apply/",
        views.application_create,
        name="application_create",
    ),
    path(
        "application/<int:pk>/accept/",
        views.application_accept,
        name="application_accept",
    ),
    path(
        "application/<int:pk>/reject/",
        views.application_reject,
        name="application_reject",
    ),
    path("applications/", views.application_list, name="application_list"),
    # Skills
    path("skills/", views.SkillListView.as_view(), name="skill_list"),
]
