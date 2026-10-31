from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_alter_post_text'),
    ]

    operations = [
        UnaccentExtension(),
        migrations.RunSQL(
            """
            CREATE TEXT SEARCH CONFIGURATION site_search (COPY = english);
            ALTER TEXT SEARCH CONFIGURATION site_search
                ALTER MAPPING FOR hword, hword_part, word WITH unaccent, english_stem;
            """,
            "DROP TEXT SEARCH CONFIGURATION site_search",
        ),
    ]
