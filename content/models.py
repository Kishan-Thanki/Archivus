# content/models.py

from django.db import models

class AboutUsContent(models.Model):
    """
    Model to store the main content for the About Us page.
    Designed to be a singleton (one entry only).
    """
    title = models.CharField(max_length=255, default="About Archivus")
    about_text = models.TextField(
        default="Welcome to Archivus! Our project is dedicated to providing seamless digital archiving solutions for everyone at DAU."
    )
    mission_title = models.CharField(max_length=255, default="Our Mission")
    mission_text = models.TextField(
        default="Since DAU is a few-years program, time is limited. We wanted to create a common portal for all current and future students—a site that serves as a comprehensive paper vault for easy access to important resources."
    )
    logo = models.ImageField(
        upload_to='about_us_assets/',
        blank=True,
        null=True,
        help_text="Optional: A logo to display on the About Us page. If empty, a placeholder will be used."
    )

    class Meta:
        verbose_name_plural = "About Us Content"
        # Optional: Add a constraint to enforce only one instance (useful for singleton models)
        # However, using .get_or_create(pk=1) in the view is generally sufficient for management.
        # constraints = [models.UniqueConstraint(fields=['id'], name='unique_about_us_content_entry')]


    def __str__(self):
        return self.title or "About Us Page Content (ID: 1)"

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return None


class TeamMember(models.Model):
    """
    Model to store individual team member details for the About Us page.
    """
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='team_members/',
        blank=True,
        null=True,
        help_text="Upload team member's photo."
    )

    class Meta:
        ordering = ['name'] # Order team members alphabetically by name
        verbose_name_plural = "Team Members"

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None