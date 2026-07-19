from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from accounts.models import Skill

from .forms import ApplicationForm, ProjectForm
from .models import Application, Category, Project


class ProjectListView(ListView):
    model = Project
    template_name = "marketplace/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        queryset = Project.objects.filter(status="open").select_related("client", "category").prefetch_related("skills")

        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        skill_id = self.request.GET.get("skill")
        if skill_id:
            queryset = queryset.filter(skills__id=skill_id)

        return queryset

    def get_context_data(self, **kwargs):
        from accounts.models import Skill

        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["skills"] = Skill.objects.all().order_by("name")
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_skill"] = self.request.GET.get("skill", "")
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "marketplace/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("client", "category", "assigned_freelancer")

    def _visible_applications(self, project):
        """Restrict applicant PII: only the project owner sees every
        application, the freelancer who applied sees their own, and everyone
        else (including anonymous visitors) sees none."""
        user = self.request.user
        if not user.is_authenticated:
            return Application.objects.none()
        qs = project.applications.select_related("freelancer", "freelancer__profile").prefetch_related(
            "freelancer__profile__skills"
        )
        if user == project.client:
            return qs
        if user.role == "freelancer":
            return qs.filter(freelancer=user)
        return Application.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        context["applications"] = self._visible_applications(project)
        context["has_applied"] = (
            user.is_authenticated
            and user.role == "freelancer"
            and project.applications.filter(freelancer=user).exists()
        )
        context["can_apply"] = (
            user.is_authenticated
            and user.role == "freelancer"
            and project.accepts_applications
            and not context["has_applied"]
        )
        return context


@login_required
def project_create(request):
    if request.user.role != "client":
        return HttpResponseForbidden("Only clients can create projects.")
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            # Persist the M2M `skills` selection — without this the chosen
            # skills are silently dropped because ProjectForm uses commit=False.
            form.save_m2m()
            messages.success(request, "Project created successfully!")
            return redirect("marketplace:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request,
        "marketplace/project_form.html",
        {
            "form": form,
            "title": "Create Project",
            "action": "Create",
        },
    )


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        messages.error(request, "You do not have permission to edit this project.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect("marketplace:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "marketplace/project_form.html",
        {
            "form": form,
            "project": project,
            "title": "Update Project",
            "action": "Update",
        },
    )


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("marketplace:project_list")

    return render(request, "marketplace/project_confirm_delete.html", {"project": project})


class CategoryListView(ListView):
    model = Category
    template_name = "marketplace/category_list.html"
    context_object_name = "categories"


class CategoryDetailView(DetailView):
    model = Category
    template_name = "marketplace/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = self.object.projects.filter(status="open").select_related("client")
        return context


@login_required
def application_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)

    if request.user.role != "freelancer":
        messages.error(request, "Only freelancers can apply to projects.")
        return redirect("marketplace:project_detail", pk=project_pk)

    if not project.accepts_applications:
        raise Http404("This project is not accepting applications.")

    if project.applications.filter(freelancer=request.user).exists():
        messages.error(request, "You have already applied to this project.")
        return redirect("marketplace:project_detail", pk=project_pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.project = project
            application.freelancer = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect("marketplace:project_detail", pk=project.pk)
    else:
        form = ApplicationForm()

    return render(
        request,
        "marketplace/application_form.html",
        {
            "form": form,
            "project": project,
        },
    )


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        messages.error(request, "You do not have permission to complete this project.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if project.status != "assigned":
        messages.error(request, "Only assigned projects can be marked as completed.")
        return redirect("marketplace:project_detail", pk=project.pk)

    project.status = "completed"
    project.save()
    messages.success(request, "Project marked as completed!")
    return redirect("marketplace:project_detail", pk=project.pk)


@login_required
@require_POST
def application_accept(request, pk):
    application = get_object_or_404(Application, pk=pk)
    project = application.project

    if project.client != request.user:
        messages.error(request, "You do not have permission to accept this application.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if application.status != "pending":
        messages.error(request, "Only pending applications can be accepted.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if not project.accepts_applications:
        messages.error(request, "This project is no longer accepting applications.")
        return redirect("marketplace:project_detail", pk=project.pk)

    with transaction.atomic():
        application.status = "accepted"
        application.save()

        project.assigned_freelancer = application.freelancer
        project.status = "assigned"
        project.save()

        project.applications.filter(status="pending").exclude(pk=pk).update(status="rejected")

    messages.success(request, "Application accepted successfully!")
    return redirect("marketplace:project_detail", pk=project.pk)


@login_required
@require_POST
def application_reject(request, pk):
    application = get_object_or_404(Application, pk=pk)
    project = application.project

    if project.client != request.user:
        messages.error(request, "You do not have permission to reject this application.")
        return redirect("marketplace:project_detail", pk=project.pk)

    if application.status != "pending":
        messages.error(request, "Only pending applications can be rejected.")
        return redirect("marketplace:project_detail", pk=project.pk)

    application.status = "rejected"
    application.save()

    messages.success(request, "Application rejected.")
    return redirect("marketplace:project_detail", pk=project.pk)


@login_required
def application_list(request):
    """Show applications: received (client) or submitted (freelancer)."""
    status_filter = request.GET.get("status", "")

    if request.user.role == "client":
        applications = (
            Application.objects.filter(project__client=request.user)
            .select_related("freelancer", "project")
            .prefetch_related("freelancer__profile__skills")
        )
    else:
        applications = (
            Application.objects.filter(freelancer=request.user)
            .select_related("project", "project__client")
            .prefetch_related("freelancer__profile__skills")
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    project_filter = request.GET.get("project", "")
    if project_filter and request.user.role == "client":
        applications = applications.filter(project_id=project_filter)

    user_projects = (
        Project.objects.filter(client=request.user) if request.user.role == "client" else Project.objects.none()
    )

    return render(
        request,
        "marketplace/application_list.html",
        {
            "applications": applications,
            "status_filter": status_filter,
            "user_projects": user_projects,
        },
    )


class SkillListView(ListView):
    model = Skill
    template_name = "marketplace/skill_list.html"
    context_object_name = "skills"
    queryset = Skill.objects.all().order_by("name")
