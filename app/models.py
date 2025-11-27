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
