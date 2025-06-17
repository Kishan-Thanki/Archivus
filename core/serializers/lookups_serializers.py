from rest_framework import serializers
from core.models import DegreeLevel, Program

class DegreeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeLevel
        fields = ['code', 'name']

class ProgramSerializer(serializers.ModelSerializer):
    degree_level_name = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'degree_level_id', 'degree_level_name']

    def get_degree_level_name(self, obj):
        return obj.degree_level.name if obj.degree_level else None