# Generated by Django 4.2 on 2023-04-04 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Team", "0002_alter_team_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(
                choices=[
                    ("Danbi", "단비"),
                    ("Darae", "다래"),
                    ("Blabla", "블라블라"),
                    ("Cheollo", "철로"),
                    ("DangE", "땅이"),
                    ("Haetae", "해태"),
                ],
                max_length=10,
                unique=True,
            ),
        ),
    ]
