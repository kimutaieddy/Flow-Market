"""
Django Admin configuration
Allows easy management of contacts and campaigns through the admin interface
"""
from django.contrib import admin
from .models import Contact, Campaign, Product, CampaignTemplate, ContactList, SentCampaign


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    list_display = ('name', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 50


@admin.register(CampaignTemplate)
class CampaignTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for Campaign Template model
    Manage saved campaign templates
    """
    list_display = ('name', 'message_preview', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'message', 'created_by')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    
    def message_preview(self, obj):
        """Show a preview of the campaign message"""
        if len(obj.message) > 60:
            return obj.message[:60] + '...'
        return obj.message
    
    message_preview.short_description = 'Message Preview'


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact List model
    Manage contact groups/lists
    """
    list_display = ('name', 'contact_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    filter_horizontal = ('contacts',)  # Nice interface for many-to-many
    ordering = ('name',)
    list_per_page = 25
    
    def contact_count_display(self, obj):
        """Display the number of contacts in the list"""
        return obj.contact_count()
    
    contact_count_display.short_description = 'Contacts Count'


@admin.register(SentCampaign)
class SentCampaignAdmin(admin.ModelAdmin):
    """
    Admin interface for Sent Campaign model
    View history of sent campaigns
    """
    list_display = ('campaign_name', 'list_name', 'recipients_count', 'status', 'sent_by', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('message', 'sent_by')
    readonly_fields = ('campaign_template', 'contact_list', 'message', 'recipients_count', 'sent_at', 'sent_by', 'api_response', 'status')
    ordering = ('-sent_at',)
    list_per_page = 25
    
    def campaign_name(self, obj):
        """Display campaign template name"""
        return obj.campaign_template.name if obj.campaign_template else 'N/A'
    
    campaign_name.short_description = 'Campaign'
    
    def list_name(self, obj):
        """Display contact list name"""
        return obj.contact_list.name if obj.contact_list else 'N/A'
    
    list_name.short_description = 'Contact List'
    
    def has_add_permission(self, request):
        """Disable manual adding (campaigns are sent via USSD/API)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Keep records for history"""
        return False
