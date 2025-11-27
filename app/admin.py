"""
Django Admin configuration
Allows easy management of contacts and campaigns through the admin interface
"""
from django.contrib import admin
from .models import Contact, Campaign


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact model
    Makes it easy to add, edit, and view contacts
    """
    # Fields to display in the list view
    list_display = ('name', 'phone_number', 'is_active', 'created_at')
    
    # Fields you can filter by
    list_filter = ('is_active', 'created_at')
    
    # Fields you can search
    search_fields = ('name', 'phone_number')
    
    # Fields that are read-only
    readonly_fields = ('created_at',)
    
    # Default ordering
    ordering = ('-created_at',)
    
    # How many contacts to show per page
    list_per_page = 50


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """
    Admin interface for Campaign model
    Allows viewing of sent campaigns and their results
    """
    # Fields to display in the list view
    list_display = ('sent_at', 'recipients_count', 'status', 'message_preview')
    
    # Fields you can filter by
    list_filter = ('status', 'sent_at')
    
    # Fields that are read-only (campaigns shouldn't be edited)
    readonly_fields = ('message', 'recipients_count', 'sent_at', 'api_response', 'status')
    
    # Default ordering
    ordering = ('-sent_at',)
    
    # How many campaigns to show per page
    list_per_page = 25
    
    def message_preview(self, obj):
        """
        Show a preview of the message (first 50 characters)
        """
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    
    message_preview.short_description = 'Message Preview'
    
    def has_add_permission(self, request):
        """
        Disable adding campaigns manually (they should be created via API)
        """
        return False
    
    def has_delete_permission(self, request, obj=None):
        """
        Keep campaign records for history
        """
        return False
