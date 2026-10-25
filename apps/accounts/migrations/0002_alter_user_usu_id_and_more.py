import django.core.validators
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="usu_id",
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="USU ID must contain digits only.", regex="^[0-9]+$"
                    )
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("email", ""), _negated=True),
                    (
                        "email",
                        django.db.models.functions.text.Lower(
                            django.db.models.functions.text.Trim("email")
                        ),
                    ),
                ),
                name="accounts_user_email_normalized",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("usu_id__isnull", True),
                    models.Q(
                        ("usu_id", django.db.models.functions.text.Trim("usu_id")),
                        ("usu_id__regex", "^[0-9]+$"),
                    ),
                    _connector="OR",
                ),
                name="accounts_user_usu_id_normalized",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("usu_id__isnull", True),
                        ("usu_review_status", "not_submitted"),
                        ("usu_reviewed_at__isnull", True),
                        ("usu_reviewed_by__isnull", True),
                    ),
                    models.Q(
                        ("is_usyd_student", True),
                        ("usu_id__isnull", False),
                        ("usu_review_status", "pending"),
                        ("usu_reviewed_at__isnull", True),
                        ("usu_reviewed_by__isnull", True),
                    ),
                    models.Q(
                        ("is_usyd_student", True),
                        ("usu_id__isnull", False),
                        ("usu_review_status__in", ("verified", "rejected")),
                        ("usu_reviewed_at__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="accounts_user_valid_usu_state",
            ),
        ),
    ]
