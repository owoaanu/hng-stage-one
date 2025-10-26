from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .models import AnalyzedString, StringAnalysis
from .filters import AnalyzedStringFilter
from .serializers import  (StringSerializer,
    StringAnalysisSerializer,
    StringCreateSerializer,
    StringListResponseSerializer,
    NaturalLanguageFilterSerializer,
    NaturalLanguageResponseSerializer
)
from .utils import StringAnalyzer

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
            if 'value' in e.detail:# and 'Not a valid string' in e.detail['value'][0]:
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

        if min_length:
            response_data['filters_applied']["min_length"] = int(min_length)

        if max_length:
            response_data['filters_applied']["max_length"] = int(max_length)


        if word_count:
            response_data['filters_applied']["word_count"] = int(word_count)

        if contains_character:
            response_data['filters_applied']["contains_character"] = contains_character

        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Custom delete method to remove a string by its 'value' field"""
        lookup_value = kwargs.get(self.lookup_field)

        try:
            instance = self.get_queryset().get(value=lookup_value)
        except AnalyzedString.DoesNotExist:
            return Response(
                {"error": f"String '{lookup_value}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Perform the deletion
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

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

@api_view(['GET', 'POST'])
def create_analyze_string(request):

    if request.method == 'GET':
        return list_strings(request)

    """Create/Analyze String - POST /strings"""
    serializer = StringCreateSerializer(data=request.data)

    if not serializer.is_valid():
        errors = serializer.errors
        if 'value' in errors:
            if 'This field is required.' in str(errors['value']):
                return Response(
                    {'error': 'Missing "value" field'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif 'Value must be a string' in str(errors['value']):
                return Response(
                    {'error': 'Invalid data type for "value" (must be string)'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    value = serializer.validated_data['value']
    properties = StringAnalyzer.analyze_string(value)

    # Check if string already exists
    if StringAnalysis.objects.filter(id=properties['sha256_hash']).exists():
        return Response(
            {'error': 'String already exists in the system'},
            status=status.HTTP_409_CONFLICT
        )

    # Create analysis
    analysis = StringAnalysis.objects.create(
        id=properties['sha256_hash'],
        value=value,
        properties=properties
    )

    return Response(
        StringAnalysisSerializer(analysis).data,
        status=status.HTTP_201_CREATED
    )

@api_view(['GET', 'DELETE'])
def get_string(request, string_value):
    """Get Specific String - GET /strings/{string_value}"""
    analysis = get_object_or_404(
        StringAnalysis,
        value=string_value
    )

    # return Response(StringAnalysisSerializer(analysis).data)
    if request.method == 'GET':
        serializer = StringAnalysisSerializer(analysis)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        analysis.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
def list_strings(request):
    """Get All Strings with Filtering - GET /strings"""
    analyses = StringAnalysis.objects.all()

    # Apply filters
    filters_applied = {}

    is_palindrome = request.GET.get('is_palindrome')
    if is_palindrome is not None:
        if is_palindrome.lower() in ['true', '1']:
            analyses = analyses.filter(properties__is_palindrome=True)
            filters_applied['is_palindrome'] = True
        elif is_palindrome.lower() in ['false', '0']:
            analyses = analyses.filter(properties__is_palindrome=False)
            filters_applied['is_palindrome'] = False

    min_length = request.GET.get('min_length')
    if min_length:
        try:
            min_length = int(min_length)
            analyses = analyses.filter(properties__length__gte=min_length)
            filters_applied['min_length'] = min_length
        except ValueError:
            return Response(
                {'error': 'Invalid min_length parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

    max_length = request.GET.get('max_length')
    if max_length:
        try:
            max_length = int(max_length)
            analyses = analyses.filter(properties__length__lte=max_length)
            filters_applied['max_length'] = max_length
        except ValueError:
            return Response(
                {'error': 'Invalid max_length parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

    word_count = request.GET.get('word_count')
    if word_count:
        try:
            word_count = int(word_count)
            analyses = analyses.filter(properties__word_count=word_count)
            filters_applied['word_count'] = word_count
        except ValueError:
            return Response(
                {'error': 'Invalid word_count parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

    contains_character = request.GET.get('contains_character')
    if contains_character:
        if len(contains_character) != 1:
            return Response(
                {'error': 'contains_character must be a single character'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Filter by character presence in frequency map
        analyses = analyses.filter(
            properties__character_frequency_map__has_key=contains_character
        )
        filters_applied['contains_character'] = contains_character

    data = StringAnalysisSerializer(analyses, many=True).data
    response_data = {
        'data': data,
        'count': len(data),
        'filters_applied': filters_applied
    }

    return Response(StringListResponseSerializer(response_data).data)

@api_view(['GET'])
def filter_by_natural_language(request):
    """Natural Language Filtering - GET /strings/filter-by-natural-language"""
    serializer = NaturalLanguageFilterSerializer(data=request.GET)

    if not serializer.is_valid():
        return Response(
            {'error': 'Unable to parse natural language query'},
            status=status.HTTP_400_BAD_REQUEST
        )

    query = serializer.validated_data['query']
    interpreted_query = StringAnalyzer.parse_natural_language_query(query)

    # Apply parsed filters
    analyses = StringAnalysis.objects.all()
    filters = interpreted_query['parsed_filters']

    for key, value in filters.items():
        if key == 'is_palindrome':
            analyses = analyses.filter(properties__is_palindrome=value)
        elif key == 'min_length':
            analyses = analyses.filter(properties__length__gte=value)
        elif key == 'max_length':
            analyses = analyses.filter(properties__length__lte=value)
        elif key == 'word_count':
            analyses = analyses.filter(properties__word_count=value)
        elif key == 'contains_character':
            analyses = analyses.filter(
                properties__character_frequency_map__has_key=value
            )

    data = StringAnalysisSerializer(analyses, many=True).data
    response_data = {
        'data': data,
        'count': len(data),
        'interpreted_query': interpreted_query
    }

    return Response(NaturalLanguageResponseSerializer(response_data).data)

@api_view(['DELETE'])
def delete_string(request, string_value):
    """Delete String - DELETE /strings/{string_value}"""
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    analysis.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)