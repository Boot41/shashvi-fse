from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Lead, LeadMessage
from .scoring import LeadScorer

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'industry', 'company_size_display', 
                   'funding_display', 'lead_score_display', 'status', 'linkedin_link', 'about_preview')
    list_filter = ('status', 'industry', 'created_at')
    search_fields = ('name', 'company', 'email', 'metadata__website', 'metadata__location', 'metadata__about')
    readonly_fields = ('created_at', 'updated_at', 'lead_score', 'get_metadata_display', 'website_link', 'about_text', 'linkedin_link')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'company', 'position', 'website_link', 'linkedin_link')
        }),
        ('Company Details', {
            'fields': ('industry', 'company_size', 'funding_amount', 'open_positions')
        }),
        ('Company Description', {
            'fields': ('about_text',),
            'classes': ('wide',)
        }),
        ('Lead Status', {
            'fields': ('status', 'lead_score', 'last_contacted')
        }),
        ('Additional Information', {
            'fields': ('notes', 'get_metadata_display')
        }),
        ('System Fields', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def company_size_display(self, obj):
        if not obj.company_size:
            return '-'
        return obj.company_size
    company_size_display.short_description = 'Company Size'

    def funding_display(self, obj):
        if not obj.funding_amount:
            return '-'
        # Format funding amount in millions/billions
        amount = float(obj.funding_amount)
        if amount >= 1_000_000_000:
            return f'${amount/1_000_000_000:.1f}B'
        elif amount >= 1_000_000:
            return f'${amount/1_000_000:.1f}M'
        else:
            return f'${amount:,.0f}'
    funding_display.short_description = 'Funding'

    def website_link(self, obj):
        if not obj.metadata or not obj.metadata.get('website'):
            return '-'
        return format_html('<a href="{}" target="_blank">{}</a>', 
                         obj.metadata['website'], obj.metadata['website'])
    website_link.short_description = 'Website'

    def about_preview(self, obj):
        if not obj.metadata or not obj.metadata.get('about'):
            return '-'
        about = obj.metadata['about']
        if len(about) > 100:
            return format_html('<span title="{}">{}&hellip;</span>', 
                             about, about[:100])
        return about
    about_preview.short_description = 'About'

    def about_text(self, obj):
        if not obj.metadata or not obj.metadata.get('about'):
            return '-'
        return format_html('<div style="max-width: 800px;">{}</div>', obj.metadata['about'])
    about_text.short_description = 'About'

    def linkedin_link(self, obj):
        if not obj.metadata or not obj.metadata.get('linkedin_url'):
            return '-'
        url = obj.metadata['linkedin_url']
        return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-yes.svg" alt="LinkedIn" style="height: 15px; width: 15px;"/> LinkedIn</a>', url)
    linkedin_link.short_description = 'LinkedIn'

    def lead_score_display(self, obj):
        if obj.lead_score is None:
            return '-'
        color = 'green' if obj.lead_score >= 70 else 'orange' if obj.lead_score >= 40 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.lead_score
        )
    lead_score_display.short_description = 'Lead Score'

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['calculate_lead_scores', 'generate_messages']

    def calculate_lead_scores(self, request, queryset):
        scorer = LeadScorer()
        updated = 0
        for lead in queryset:
            company_data = {
                'funding_amount': float(lead.funding_amount) if lead.funding_amount else 0,
                'industry': lead.industry,
                'hiring_data': {'open_positions': lead.open_positions}
            }
            lead.lead_score = scorer.calculate_total_score(company_data)
            lead.save()
            updated += 1
        
        self.message_user(request, f"Successfully updated scores for {updated} leads.")
    calculate_lead_scores.short_description = "Calculate lead scores for selected leads"

    def generate_messages(self, request, queryset):
        from .message_generator import generate_messages
        generated = 0
        for lead in queryset:
            messages = generate_messages(lead)
            LeadMessage.objects.create(
                lead=lead,
                linkedin_message=messages['linkedin_message'],
                email_content=messages['email']
            )
            generated += 1
        
        self.message_user(request, f"Successfully generated messages for {generated} leads.")
    generate_messages.short_description = "Generate messages for selected leads"

@admin.register(LeadMessage)
class LeadMessageAdmin(admin.ModelAdmin):
    list_display = ('lead', 'created_at', 'message_preview')
    list_filter = ('created_at',)
    search_fields = ('lead__name', 'lead__company', 'linkedin_message', 'email_content')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.linkedin_message[:100] + '...' if len(obj.linkedin_message) > 100 else obj.linkedin_message
    message_preview.short_description = 'LinkedIn Message Preview'
