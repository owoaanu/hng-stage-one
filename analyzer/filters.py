# your_app/filters.py
import django_filters
from .models import AnalyzedString


class AnalyzedStringFilter(django_filters.FilterSet):
    # Example 1: Exact match filter for 'length' (e.g., ?length=10)
    min_length = django_filters.NumberFilter(field_name='length', lookup_expr='gte')
    max_length = django_filters.NumberFilter(field_name='length', lookup_expr='lte')

    # Example 2: Range filter for 'word_count' (e.g., ?word_count__gte=5)
    word_count = django_filters.NumberFilter(field_name='word_count', lookup_expr='exact')
    contains_character = django_filters.CharFilter(field_name='value', lookup_expr='icontains')

    # Example 3: Boolean filter for 'is_palindrome' (e.g., ?is_palindrome=true)
    is_palindrome = django_filters.BooleanFilter(field_name='is_palindrome')

    class Meta:
        model = AnalyzedString
        # You can also list fields for simple exact lookups
        fields = ['is_palindrome', "min_length", "max_length", "word_count", "contains_character"]

        