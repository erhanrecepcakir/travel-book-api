# Generated by Django 3.0.5 on 2020-05-05 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200503_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('begins', models.DateField()),
                ('ends', models.DateField()),
                ('budget', models.DecimalField(decimal_places=2, max_digits=10)),
                ('done', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('visits', models.ManyToManyField(to='core.Visit')),
            ],
        ),
    ]