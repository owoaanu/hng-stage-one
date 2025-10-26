from rest_framework import serializers
from .models import AnalyzedString, StringAnalysis
from .utils import describe_string, hash_string


class StrictCharField(serializers.CharField):
    def to_internal_value(self, data):
        # 'data' is the raw value coming from the JSON parser (int, bool, etc.)
        if not isinstance(data, str):
            raise serializers.ValidationError("Not a valid string. Value must be a JSON string (in quotes).")
        return super().to_internal_value(data)
    
class StringSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    value = StrictCharField(required=True)
    length = serializers.IntegerField(read_only=True)
    is_palindrome = serializers.BooleanField(read_only=True)
    unique_characters = serializers.IntegerField(read_only=True)
    word_count = serializers.IntegerField(read_only=True)
    character_frequency_map = serializers.JSONField(read_only=True)

    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Not a valid string.")
        return value


    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'length', 'is_palindrome', 'unique_characters', 'word_count', 'character_frequency_map', 'created_at']
        read_only_fields = ('id', 'length', 'is_palindrome', 'unique_characters', 'word_count', 'character_frequency_map', 'created_at')

    def create(self, validated_data):

        input_string = validated_data.get('value')
        if AnalyzedString.objects.filter(pk=hash_string(input_string)):
            raise serializers.ValidationError(
                {"detail": "String already exists in the system."},
                code="conflict" # Custom code helps identify the error later
            )

        analysis_results = describe_string(input_string)

        validated_data['id'] = analysis_results['sha256_hash']
        validated_data['length'] = analysis_results['length']
        validated_data['is_palindrome'] = analysis_results['is_palindrome']
        validated_data['unique_characters'] = analysis_results['unique_characters']
        validated_data['word_count'] = analysis_results['word_count']
        validated_data['character_frequency_map'] = analysis_results['character_frequency_map']

        return AnalyzedString.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        properties_fields = [
            'length', 'is_palindrome', 'unique_characters',
            'word_count', 'sha256_hash', 'character_frequency_map'
        ]

        properties = dict()
        for field in properties_fields:
            if field == 'sha256_hash':
                properties[field] = representation['id']
                continue
            properties[field] = representation.pop(field)

        representation['properties'] = properties

        representation['created_at'] = representation.pop('created_at')

        return representation

class StringAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['id', 'properties', 'created_at']

class StringCreateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, max_length=10000)

    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string")
        if not value.strip():
            raise serializers.ValidationError("Value cannot be empty")
        return value

class StringListResponseSerializer(serializers.Serializer):
    data = StringAnalysisSerializer(many=True)
    count = serializers.IntegerField()
    filters_applied = serializers.DictField(required=False)

class NaturalLanguageFilterSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=500)

    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError("Query cannot be empty")
        return value

class NaturalLanguageResponseSerializer(serializers.Serializer):
    data = StringAnalysisSerializer(many=True)
    count = serializers.IntegerField()
    interpreted_query = serializers.DictField()
