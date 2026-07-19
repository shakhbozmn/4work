from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import View

from marketplace.models import Application, Project

from .forms import CustomAuthenticationForm, CustomUserCreationForm, ProfileForm
from .models import Profile, User


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        # Create profile for new user
        Profile.objects.get_or_create(user=self.object)
        messages.success(self.request, "Registration successful! Welcome to 4work.")
        return response


class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, "auth/login.html", {"form": form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login successful!")
            next_url = request.GET.get("next") or reverse_lazy("accounts:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
        return render(request, "auth/login.html", {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("accounts:login")


@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    context = {
        "profile_user": user,
        "profile": profile,
    }
    return render(request, "accounts/profile_detail.html", context)


@login_required
def dashboard(request):
    """Role-based dashboard: clients see their projects; freelancers see their applications."""
    if request.user.role == "client":
        projects = Project.objects.filter(client=request.user).order_by("-created_at")
        pending_applications = Application.objects.filter(project__client=request.user, status="pending").count()
        stats = {
            "total_projects": projects.count(),
            "active_projects": projects.filter(status__in=["open", "reviewing", "assigned"]).count(),
            "pending_applications": pending_applications,
            "total_spent": sum(p.budget for p in projects.filter(status="completed")),
        }
        recent_applications = (
            Application.objects.filter(project__client=request.user)
            .select_related("freelancer", "project")
            .order_by("-created_at")[:10]
        )
        return render(
            request,
            "dashboard/client_dashboard.html",
            {
                "recent_projects": projects[:10],
                "stats": stats,
                "recent_applications": recent_applications,
            },
        )
    else:
        applications = (
            Application.objects.filter(freelancer=request.user).select_related("project").order_by("-created_at")
        )
        total_earned = (
            Project.objects.filter(
                assigned_freelancer=request.user,
                status="completed",
            ).aggregate(
                total=Sum("budget")
            )["total"]
            or 0
        )
        stats = {
            "total_applications": applications.count(),
            "accepted_applications": applications.filter(status="accepted").count(),
            "active_jobs": applications.filter(status="accepted", project__status="assigned").count(),
            "total_earned": total_earned,
        }

        # Get skill-matched projects for freelancers
        user_skills = request.user.profile.skills.all() if hasattr(request.user, "profile") else []
        matched_projects = []
        if user_skills:
            matched_projects = (
                Project.objects.filter(status="open", skills__in=user_skills)
                .exclude(applications__freelancer=request.user)
                .distinct()[:5]
            )

        return render(
            request,
            "dashboard/freelancer_dashboard.html",
            {
                "recent_applications": applications[:10],
                "stats": stats,
                "matched_projects": matched_projects,
            },
        )


@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:profile_detail", username=request.user.username)
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, "accounts/profile_update.html", {"form": form})
