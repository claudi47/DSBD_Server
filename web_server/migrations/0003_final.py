from django.db import migrations, models


def create_settings(apps, schema_editor):
    if schema_editor.connection.alias != 'parser':
        return
    settings = apps.get_model("web_server", "Settings")
    settings.objects.create(goldbet_research=True, bwin_research=True)

class Migration(migrations.Migration):

    dependencies = [
        ('web_server', '0002_auto_20211226_1752')
    ]

    operations = [
        migrations.RunPython(create_settings)
    ]