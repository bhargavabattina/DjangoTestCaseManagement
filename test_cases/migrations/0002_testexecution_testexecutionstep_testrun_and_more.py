# Generated by Django 5.2.3 on 2025-07-01 18:09

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("test_cases", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TestExecution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_executed", "Not Executed"),
                            ("in_progress", "In Progress"),
                            ("passed", "Passed"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                            ("blocked", "Blocked"),
                        ],
                        default="not_executed",
                        max_length=20,
                    ),
                ),
                ("execution_date", models.DateTimeField(blank=True, null=True)),
                ("comments", models.TextField(blank=True)),
                (
                    "execution_time_minutes",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "executor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="test_executions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "testcase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="test_executions",
                        to="test_cases.testcase",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Test Executions",
                "ordering": ["testcase__priority", "execution_date"],
            },
        ),
        migrations.CreateModel(
            name="TestExecutionStep",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("step_number", models.PositiveIntegerField()),
                ("step_description", models.TextField()),
                ("expected_result", models.TextField()),
                ("actual_result", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_executed", "Not Executed"),
                            ("passed", "Passed"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        default="not_executed",
                        max_length=20,
                    ),
                ),
                ("execution_date", models.DateTimeField(blank=True, null=True)),
                ("comments", models.TextField(blank=True)),
                (
                    "test_execution",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="execution_steps",
                        to="test_cases.testexecution",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Test Execution Steps",
                "ordering": ["test_execution", "step_number"],
            },
        ),
        migrations.CreateModel(
            name="TestRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("scheduled_date", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_test_runs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Test Runs",
                "ordering": ["-created_date"],
            },
        ),
        migrations.AddField(
            model_name="testexecution",
            name="test_run",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="test_executions",
                to="test_cases.testrun",
            ),
        ),
        migrations.CreateModel(
            name="TestSuite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "created_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_test_suites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "test_cases",
                    models.ManyToManyField(
                        related_name="test_suites", to="test_cases.testcase"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Test Suites",
                "ordering": ["-created_date"],
            },
        ),
    ]
