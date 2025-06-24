# content/serializers.py

from rest_framework import serializers
from .models import AboutUsContent, TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the TeamMember model, providing absolute URL for the image.
    """
    image = serializers.SerializerMethodField() # This will call get_image method

    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'image'] # Include 'id' for frontend keying

    def get_image(self, obj):
        # Build absolute URL using the request context passed from the view
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url # Fallback if no request context (e.g., in shell)
        return None # Return None if no image is uploaded


class AboutUsContentSerializer(serializers.ModelSerializer):
    """
    Serializer for the AboutUsContent model, including nested team members
    and absolute URL for the main logo.
    """
    team_members = serializers.SerializerMethodField() # This will call get_team_members method
    logo_url = serializers.SerializerMethodField() # This will call get_logo_url method

    class Meta:
        model = AboutUsContent
        fields = [
            'id', # Include 'id' if needed for any reason, though not directly used by frontend in this case
            'title',
            'about_text',
            'mission_title',
            'mission_text',
            'logo_url', # The field that will contain the logo's URL
            'team_members' # The field that will contain the list of serialized team members
        ]

    def get_team_members(self, obj):
        # Fetch all TeamMember instances
        team_members = TeamMember.objects.all()
        # Serialize them using TeamMemberSerializer, passing the request context
        return TeamMemberSerializer(team_members, many=True, context=self.context).data

    def get_logo_url(self, obj):
        # Similar logic as get_image for team members' images
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None # Return None if no logo is uploaded