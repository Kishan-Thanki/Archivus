# content/admin.py
from django.contrib import admin
from .models import AboutUsContent, TeamMember
from django.utils.html import format_html # Import format_html for clickable URLs

@admin.register(AboutUsContent)
class AboutUsContentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AboutUsContent model.
    Allows managing the singleton About Us page content.
    """
    # Display these fields in the list view of the admin
    list_display = ('title', 'logo_url_display', 'id')
    # Fields that should be read-only in the edit form
    readonly_fields = ('logo_url_display',)
    # Organize fields into sections in the edit form
    fieldsets = (
        (None, {
            'fields': ('title', 'about_text', 'mission_title', 'mission_text', 'logo'),
        }),
    )

    def logo_url_display(self, obj):
        """
        Custom method to display the logo URL as a clickable link in the admin list.
        """
        if obj.logo and hasattr(obj.logo, 'url'):
            return format_html(f'<a href="{obj.logo.url}" target="_blank">{obj.logo.url}</a>')
        return "No logo uploaded"
    logo_url_display.short_description = "Logo URL" # Column header in admin list

    def has_add_permission(self, request):
        # Allow adding only if no instance exists
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Optionally, prevent deletion too, or only allow it if it's the only one
        return False  # Or make it smarter if you want deletion control


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TeamMember model.
    Allows managing individual team members.
    """
    # Display these fields in the list view of the admin
    list_display = ('name', 'role', 'image_url_display', 'id')
    # Fields to search by in the admin
    search_fields = ('name', 'role')
    # Fields to filter by in the admin sidebar
    list_filter = ('role',)
    # Fields that should be read-only in the edit form
    readonly_fields = ('image_url_display',)

    def image_url_display(self, obj):
        """
        Custom method to display the team member's image URL as a clickable link.
        """
        if obj.image and hasattr(obj.image, 'url'):
            return format_html(f'<a href="{obj.image.url}" target="_blank">{obj.image.url}</a>')
        return "No image uploaded"
    image_url_display.short_description = "Image URL" # Column header in admin list

