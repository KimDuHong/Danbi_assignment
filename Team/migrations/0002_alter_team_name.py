# Generated by Django 4.2 on 2023-04-04 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Team", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(
                choices=[
                    ("단비", "Danbi"),
                    ("다래", "Darae"),
                    ("블라블라", "Blabla"),
                    ("철로", "Cheollo"),
                    ("땅이", "Dange"),
                    ("해태", "Haetae"),
                ],
                max_length=10,
                unique=True,
            ),
        ),
    ]