"""
Database models for the application
Two simple models: Contact and Campaign
"""
from django.db import models


class Contact(models.Model):
    """
    Model to store contact information for SMS campaigns
    Each contact has a phone number and name
    """
    # Phone number in international format (e.g., +254712345678)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Phone number in international format (e.g., +254712345678)"
    )
    
    # Contact name
    name = models.CharField(
        max_length=100,
        help_text="Contact's name"
    )
    
    # When was this contact added?
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Is this contact active? (Can be used to exclude contacts from campaigns)
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this contact should receive SMS"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest contacts first
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
    
    def __str__(self):
        """String representation of the contact"""
        return f"{self.name} ({self.phone_number})"


class Campaign(models.Model):
    """
    Model to log SMS campaigns
    Tracks when campaigns were sent and to how many contacts
    """
    # Campaign details
    message = models.TextField(
        help_text="The SMS message that was sent"
    )
    
    # How many contacts received the message?
    recipients_count = models.IntegerField(
        default=0,
        help_text="Number of contacts who received the SMS"
    )
    
    # When was this campaign sent?
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Response from Africa's Talking API
    api_response = models.TextField(
        blank=True,
        null=True,
        help_text="Response from Africa's Talking API"
    )
    
    # Success or failure?
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ],
        default='success'
    )
    
    class Meta:
        ordering = ['-sent_at']  # Most recent campaigns first
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
    
    def __str__(self):
        """String representation of the campaign"""
        return f"Campaign on {self.sent_at.strftime('%Y-%m-%d %H:%M')} - {self.recipients_count} recipients"


# =============================
# Product Model
# =============================
class Product(models.Model):
    """
    Model to store product information
    Each product has a name, description, price, and created date
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Product name"
    )

    description = models.TextField(
        blank=True,
        help_text="Product description"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price (e.g., 99.99)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time the product was added"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether the product is active and available"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - KES {self.price}"


# =============================
# Campaign Template Model
# =============================
class CampaignTemplate(models.Model):
    """
    Model to store campaign templates (pre-created SMS campaigns)
    Users can create and save campaigns, then send them later
    """
    name = models.CharField(
        max_length=100,
        help_text="Campaign name (e.g., 'New Product', 'Valentines Hampers')"
    )
    
    message = models.TextField(
        help_text="SMS message template. Use [Name] for personalization."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number of user who created this campaign"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this campaign template is active"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Campaign Template"
        verbose_name_plural = "Campaign Templates"
    
    def __str__(self):
        return f"{self.name}"


# =============================
# Contact List Model
# =============================
class ContactList(models.Model):
    """
    Model to group contacts into lists (e.g., VIP, Test List, All Contacts)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="List name (e.g., 'VIP Contacts', 'Test List')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of this contact list"
    )
    
    contacts = models.ManyToManyField(
        Contact,
        related_name='contact_lists',
        blank=True,
        help_text="Contacts in this list"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this list is active"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Contact List"
        verbose_name_plural = "Contact Lists"
    
    def __str__(self):
        return f"{self.name} ({self.contacts.count()} contacts)"
    
    def contact_count(self):
        """Return the number of contacts in this list"""
        return self.contacts.filter(is_active=True).count()


# =============================
# Sent Campaign Log Model
# =============================
class SentCampaign(models.Model):
    """
    Model to log sent SMS campaigns with details
    """
    campaign_template = models.ForeignKey(
        CampaignTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The campaign template that was sent"
    )
    
    contact_list = models.ForeignKey(
        ContactList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The contact list that received the campaign"
    )
    
    message = models.TextField(
        help_text="The actual SMS message that was sent"
    )
    
    recipients_count = models.IntegerField(
        default=0,
        help_text="Number of recipients"
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    sent_by = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number of user who sent this campaign"
    )
    
    api_response = models.TextField(
        blank=True,
        null=True,
        help_text="Response from Africa's Talking API"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ],
        default='success'
    )
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Sent Campaign"
        verbose_name_plural = "Sent Campaigns"
    
    def __str__(self):
        return f"{self.campaign_template.name if self.campaign_template else 'Campaign'} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
