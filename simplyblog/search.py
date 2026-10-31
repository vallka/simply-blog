from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, Func, TextField, Value

# Created in blog/migrations/0016_search_config.py: english + unaccent
SEARCH_CONFIG = 'site_search'

# Postgres keeps DJI_0456.jpg or /C1/foto/Valencia as one token, split them
SEPARATORS = '/._'
SPACES = ' ' * len(SEPARATORS)


def full_text_search(queryset, fields, q):
    """Filter queryset by websearch-style query q over text fields, annotate rank"""
    q = (q or '').translate(str.maketrans(SEPARATORS, SPACES))
    split_fields = [
        Func(F(field), Value(SEPARATORS), Value(SPACES), function='translate', output_field=TextField())
        for field in fields
    ]
    vector = SearchVector(*split_fields, config=SEARCH_CONFIG)
    query = SearchQuery(q, search_type='websearch', config=SEARCH_CONFIG)

    return queryset.annotate(search=vector, rank=SearchRank(vector, query)).filter(search=query)
