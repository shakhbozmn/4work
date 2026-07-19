from django.contrib.auth import get_user_model
from django.test import TestCase

from marketplace.models import Application, Category, Project

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test cases for Category model"""

    def setUp(self):
        self.category = Category.objects.create(name="Web Development", description="Web development projects")

    def test_category_creation(self):
        """Test that a category can be created successfully"""
        self.assertEqual(self.category.name, "Web Development")
        self.assertEqual(self.category.description, "Web development projects")

    def test_category_str_method(self):
        """Test __str__ method of Category model"""
        self.assertEqual(str(self.category), "Web Development")

    def test_category_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.category.get_absolute_url()
        self.assertEqual(url, f"/marketplace/category/{self.category.pk}/")


class ProjectModelTest(TestCase):
    """Test cases for Project model"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_project_creation(self):
        """Test that a project can be created successfully"""
        self.assertEqual(self.project.title, "Test Project")
        self.assertEqual(self.project.description, "Test project description")
        self.assertEqual(self.project.budget, 500.00)

    def test_project_str_method(self):
        """Test __str__ method of Project model"""
        self.assertEqual(str(self.project), "Test Project")

    def test_project_default_status(self):
        """Test that default status is open"""
        self.assertEqual(self.project.status, "open")

    def test_project_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.project.get_absolute_url()
        self.assertEqual(url, f"/marketplace/project/{self.project.id}/")

    def test_project_client_relationship(self):
        """Test that project belongs to client"""
        self.assertEqual(self.project.client, self.client_user)

    def test_project_category_relationship(self):
        """Test that project belongs to category"""
        self.assertEqual(self.project.category, self.category)

    def test_project_freelancer_assignment(self):
        """Test that project can be assigned to freelancer"""
        freelancer = User.objects.create_user(
            username="freelancer",
            email="freelancer@example.com",
            password="testpass123",
            role="freelancer",
        )
        self.project.assigned_freelancer = freelancer
        self.project.status = "assigned"
        self.project.save()

        self.assertEqual(self.project.assigned_freelancer, freelancer)
        self.assertEqual(self.project.status, "assigned")


class ApplicationModelTest(TestCase):
    """Test cases for Application model"""

    def setUp(self):
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
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )
        self.application = Application.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_budget=300.00,
            proposed_timeline=7,
            cover_letter="I am interested in this project",
        )

    def test_application_creation(self):
        """Test that an application can be created successfully"""
        self.assertEqual(self.application.project, self.project)
        self.assertEqual(self.application.freelancer, self.freelancer_user)
        self.assertEqual(self.application.proposed_budget, 300.00)
        self.assertEqual(self.application.cover_letter, "I am interested in this project")

    def test_application_str_method(self):
        """Test __str__ method of Application model"""
        expected = f"{self.freelancer_user.username} - {self.project.title}"
        self.assertEqual(str(self.application), expected)

    def test_application_default_status(self):
        """Test that default status is pending"""
        self.assertEqual(self.application.status, "pending")

    def test_application_unique_constraint(self):
        """Test that duplicate applications are prevented"""
        with self.assertRaises(Exception):
            Application.objects.create(
                project=self.project,
                freelancer=self.freelancer_user,
                proposed_budget=400.00,
                proposed_timeline=10,
                cover_letter="Another application",
            )

    def test_application_project_relationship(self):
        """Test that application belongs to project"""
        self.assertEqual(self.application.project, self.project)

    def test_application_freelancer_relationship(self):
        """Test that application belongs to freelancer"""
        self.assertEqual(self.application.freelancer, self.freelancer_user)


class ProjectIntegrationTest(TestCase):
    """Integration tests for Project and related models"""

    def setUp(self):
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
        self.category = Category.objects.create(name="Web Development", description="Web development projects")
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            budget=500.00,
            client=self.client_user,
            category=self.category,
        )

    def test_project_with_multiple_applications(self):
        """Test that a project can have multiple applications"""
        freelancer2 = User.objects.create_user(
            username="freelancer2",
            email="freelancer2@example.com",
            password="testpass123",
            role="freelancer",
        )

        Application.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_budget=300.00,
            proposed_timeline=7,
            cover_letter="Application 1",
        )
        Application.objects.create(
            project=self.project,
            freelancer=freelancer2,
            proposed_budget=400.00,
            proposed_timeline=10,
            cover_letter="Application 2",
        )

        self.assertEqual(self.project.applications.count(), 2)

    def test_freelancer_with_multiple_applications(self):
        """Test that a freelancer can apply to multiple projects"""
        project2 = Project.objects.create(
            title="Test Project 2",
            description="Another test project",
            budget=600.00,
            client=self.client_user,
            category=self.category,
        )

        Application.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_budget=300.00,
            proposed_timeline=7,
            cover_letter="Application 1",
        )
        Application.objects.create(
            project=project2,
            freelancer=self.freelancer_user,
            proposed_budget=400.00,
            proposed_timeline=10,
            cover_letter="Application 2",
        )

        self.assertEqual(self.freelancer_user.applications.count(), 2)

    def test_category_with_multiple_projects(self):
        """Test that a category can have multiple projects"""
        Project.objects.create(
            title="Test Project 2",
            description="Another test project",
            budget=600.00,
            client=self.client_user,
            category=self.category,
        )

        self.assertEqual(self.category.projects.count(), 2)
