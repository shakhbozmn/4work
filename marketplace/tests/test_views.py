from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from marketplace.models import Application, Category, Project

User = get_user_model()


class ProjectListViewTest(TestCase):
    """Test cases for project list view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_project_list_page_loads(self):
        """Test that project list page loads successfully"""
        response = self.client.get(reverse("marketplace:project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/project_list.html")

    def test_project_list_displays_projects(self):
        """Test that project list displays projects"""
        response = self.client.get(reverse("marketplace:project_list"))
        self.assertContains(response, "Test Project")
        self.assertContains(response, "Test project description")

    def test_project_list_search(self):
        """Test project search functionality"""
        response = self.client.get(reverse("marketplace:project_list"), {"search": "Test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")

    def test_project_list_category_filter(self):
        """Test project category filter"""
        response = self.client.get(reverse("marketplace:project_list"), {"category": self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")


class ProjectDetailViewTest(TestCase):
    """Test cases for project detail view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_project_detail_page_loads(self):
        """Test that project detail page loads successfully"""
        response = self.client.get(reverse("marketplace:project_detail", args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/project_detail.html")

    def test_project_detail_displays_project_info(self):
        """Test that project detail displays project information"""
        response = self.client.get(reverse("marketplace:project_detail", args=[self.project.id]))
        self.assertContains(response, "Test Project")
        self.assertContains(response, "Test project description")
        self.assertContains(response, "500.00")

    def test_project_detail_404_for_invalid_id(self):
        """Test that project detail returns 404 for invalid id"""
        response = self.client.get(reverse("marketplace:project_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)


class ProjectCreateViewTest(TestCase):
    """Test cases for project create view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )

    def test_project_create_requires_login(self):
        """Test that project creation requires login"""
        response = self.client.get(reverse("marketplace:project_create"))
        self.assertEqual(response.status_code, 302)

    def test_project_create_page_loads_for_client(self):
        """Test that project create page loads for client user"""
        self.client.login(username="client", password="testpass123")
        response = self.client.get(reverse("marketplace:project_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/project_form.html")

    def test_project_create_with_valid_data(self):
        """Test project creation with valid data"""
        self.client.login(username="client", password="testpass123")
        response = self.client.post(
            reverse("marketplace:project_create"),
            {
                "title": "New Project",
                "description": "New project description",
                "budget": "800.00",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(title="New Project").exists())


class ApplicationCreateViewTest(TestCase):
    """Test cases for application create view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.freelancer_user = User.objects.create_user(
            username="freelancer",
            email="freelancer@example.com",
            password="testpass123",
            role="freelancer",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_application_create_requires_login(self):
        """Test that application creation requires login"""
        response = self.client.get(reverse("marketplace:application_create", args=[self.project.id]))
        self.assertEqual(response.status_code, 302)

    def test_application_create_page_loads_for_freelancer(self):
        """Test that application create page loads for freelancer user"""
        self.client.login(username="freelancer", password="testpass123")
        response = self.client.get(reverse("marketplace:application_create", args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/application_form.html")

    def test_application_create_with_valid_data(self):
        """Test application creation with valid data"""
        self.client.login(username="freelancer", password="testpass123")
        response = self.client.post(
            reverse("marketplace:application_create", args=[self.project.id]),
            {
                "proposed_budget": "300.00",
                "proposed_timeline": "7",
                "cover_letter": "I am interested in this project",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Application.objects.filter(freelancer=self.freelancer_user).exists())

    def test_application_prevents_duplicates(self):
        """Test that duplicate applications are prevented"""
        self.client.login(username="freelancer", password="testpass123")

        # Create first application
        Application.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_budget=300.00,
            proposed_timeline=7,
            cover_letter="First application",
        )

        # Try to create second application
        self.client.post(
            reverse("marketplace:application_create", args=[self.project.id]),
            {
                "proposed_budget": "400.00",
                "proposed_timeline": "10",
                "cover_letter": "Second application",
            },
        )

        # Should not create duplicate
        self.assertEqual(Application.objects.filter(freelancer=self.freelancer_user).count(), 1)


class CategoryListViewTest(TestCase):
    """Test cases for category list view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")

    def test_category_list_page_loads(self):
        """Test that category list page loads successfully"""
        response = self.client.get(reverse("marketplace:category_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/category_list.html")

    def test_category_list_displays_categories(self):
        """Test that category list displays categories"""
        response = self.client.get(reverse("marketplace:category_list"))
        self.assertContains(response, "Web Development")


class CategoryDetailViewTest(TestCase):
    """Test cases for category detail view"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_category_detail_page_loads(self):
        """Test that category detail page loads successfully"""
        response = self.client.get(reverse("marketplace:category_detail", args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "marketplace/category_detail.html")

    def test_category_detail_displays_projects(self):
        """Test that category detail displays projects in that category"""
        response = self.client.get(reverse("marketplace:category_detail", args=[self.category.pk]))
        self.assertContains(response, "Test Project")
