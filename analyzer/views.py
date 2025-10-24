from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .models import AnalyzedString
from .filters import AnalyzedStringFilter
from .serializers import StringSerializer

import re
import logging 

logger = logging.getLogger(__name__)
# Create your views here.

class StringAnalyzerViewSet(viewsets.ModelViewSet):
    queryset = AnalyzedString.objects.all()
    serializer_class = StringSerializer
    lookup_field = 'value'
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyzedStringFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if 'value' in e.detail and 'Not a valid string' in e.detail['value'][0]:
                return Response(
                    {"value": ["'value' (must be string) "]},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            else:
                raise e
        try:
            self.perform_create(serializer)
        except ValidationError as e:
            print(e.get_codes()['detail'])
            if e.get_codes()['detail'] == "conflict":
                return Response(
                    {"data-conflict": ["the provided string already exists"]},
                    status=status.HTTP_409_CONFLICT
                )
                # raise e

        # 3. Return a successful response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, **kwargs):
        # try:
        string= self.get_object()
        # except
        if not string:
            return Response({'error' : 'String does not exist in the system'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StringSerializer(string)
        return Response(serializer.data, status=HTTP_200_OK)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        is_palindrome = request.query_params.get('is_palindrome')
        min_length = request.query_params.get('min_length')
        max_length = request.query_params.get('max_length')
        word_count = request.query_params.get('word_count')
        contains_character = request.query_params.get('contains_character')

        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "data": serializer.data,
            "count": len(serializer.data),
            "filters_applied": {
           },
        }

        if bool(is_palindrome):
            response_data['filters_applied']["is_palindrome"] = bool(is_palindrome)

        if max_length:
            response_data['filters_applied']["max_length"] = int(max_length)

        if min_length:
            response_data['filters_applied']["min_length"] = int(min_length)

        if word_count:
            response_data['filters_applied']["word_count"] = int(word_count)

        if contains_character:
            response_data['filters_applied']["contains_character"] = contains_character

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='filter-by-natural-language')
    def natural_language_filter(self, request):
        query = request.query_params.get('query', '').lower()

        if not query:
            return Response(
                {"error": "Query parameter 'query' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            filters = self._parse_query(query)
            queryset = self._apply_filters(self.get_queryset(), filters)
            serializer = self.get_serializer(queryset, many=True)

            return Response({
                "data": serializer.data,
                "count": len(serializer.data),
                "interpreted_query": {
                    "original": request.query_params.get('query'),
                    "parsed_filters": filters
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _parse_query(self, query: str) -> dict:
        """Parse natural language into filters using regex patterns"""
        filters = {}

        # Palindrome detection
        if re.search(r'\bpalindrom(e|ic)\b', query):
            filters['is_palindrome'] = True

        # Word count
        if 'single word' in query or 'one word' in query:
            filters['word_count'] = 1
        elif match := re.search(r'(\d+)\s*word', query):
            filters['word_count'] = int(match.group(1))

        # Length filters
        if match := re.search(r'longer than (\d+)', query):
            filters['min_length'] = int(match.group(1)) + 1
        elif match := re.search(r'at least (\d+) characters?', query):
            filters['min_length'] = int(match.group(1))
        elif match := re.search(r'minimum (?:length|of) (\d+)', query):
            filters['min_length'] = int(match.group(1))

        if match := re.search(r'shorter than (\d+)', query):
            filters['max_length'] = int(match.group(1)) - 1
        elif match := re.search(r'at most (\d+) characters?', query):
            filters['max_length'] = int(match.group(1))
        elif match := re.search(r'maximum (?:length|of) (\d+)', query):
            filters['max_length'] = int(match.group(1))

        # Character contains
        if match := re.search(r'contain(?:s|ing)?(?: the letter)? ([a-z])\b', query):
            filters['contains_character'] = match.group(1)
        elif 'first vowel' in query:
            filters['contains_character'] = 'a'
        elif match := re.search(r'letter ([a-z])\b', query):
            filters['contains_character'] = match.group(1)

        if not filters:
            raise ValueError("Unable to parse natural language query")

        return filters

    def _apply_filters(self, queryset, filters):
        """Apply parsed filters to queryset"""
        if 'is_palindrome' in filters:
            queryset = queryset.filter(is_palindrome=filters['is_palindrome'])
        if 'min_length' in filters:
            queryset = queryset.filter(length__gte=filters['min_length'])
        if 'max_length' in filters:
            queryset = queryset.filter(length__lte=filters['max_length'])
        if 'word_count' in filters:
            queryset = queryset.filter(word_count=filters['word_count'])
        if 'contains_character' in filters:
            queryset = queryset.filter(value__icontains=filters['contains_character'])

        return queryset