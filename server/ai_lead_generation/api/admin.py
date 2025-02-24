from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.conf import settings
import groq
import os
from dotenv import load_dotenv
from .models import Lead, LeadMessage, Outreach

load_dotenv()

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'industry', 'company_size_display', 
                   'funding_display', 'lead_score_display', 'status', 'linkedin_url', 'has_outreach')
    list_filter = ('status', 'industry', 'created_at')
    search_fields = ('name', 'company', 'email', 'industry', 'metadata__linkedin_url')
    readonly_fields = ('created_at', 'updated_at', 'lead_score', 'generate_messages_button', 'linkedin_url')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'company', 'position', 'linkedin_url')
        }),
        ('Company Details', {
            'fields': ('industry', 'company_size', 'funding_amount', 'open_positions')
        }),
        ('Message Generation', {
            'fields': ('generate_messages_button',),
        }),
        ('Lead Status', {
            'fields': ('status', 'lead_score', 'last_contacted')
        }),
        ('Additional Information', {
            'fields': ('notes', 'metadata')
        }),
        ('System Fields', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:lead_id>/generate-messages/',
                self.admin_site.admin_view(self.generate_messages_view),
                name='generate-lead-messages',
            ),
        ]
        return custom_urls + urls

    def generate_messages_button(self, obj):
        if obj.pk:
            html = '''
                <button type="button" onclick="generateMessages_{id}()" class="button">
                Generate Email & LinkedIn Message</button>
                <div id="messages-result-{id}"></div>
                <script>
                function generateMessages_{id}() {{
                    const button = document.querySelector('button[onclick="generateMessages_{id}()"]');
                    const resultDiv = document.getElementById('messages-result-{id}');
                    button.disabled = true;
                    button.textContent = 'Generating...';
                    resultDiv.innerHTML = '<div style="margin-top: 10px;">Generating messages...</div>';
                    
                    fetch('/admin/api/lead/{id}/generate-messages/')
                    .then(response => response.json())
                    .then(data => {{
                        button.disabled = false;
                        button.textContent = 'Generate Email & LinkedIn Message';
                        resultDiv.innerHTML = '<div style="margin-top: 10px;">' +
                            'Messages generated successfully! ' +
                            'View them in the <a href="/admin/api/outreach/">Outreach section</a>' +
                            '</div>';
                    }})
                    .catch(error => {{
                        button.disabled = false;
                        button.textContent = 'Generate Email & LinkedIn Message';
                        resultDiv.innerHTML = '<div style="margin-top: 10px; color: red;">' +
                            'Error generating messages. Please try again.' +
                            '</div>';
                    }});
                }}
                </script>
            '''.format(id=obj.pk)
            return mark_safe(html)
        return "Save the lead first to generate messages"
    generate_messages_button.short_description = "Generate Messages"
    generate_messages_button.allow_tags = True

    def linkedin_url(self, obj):
        """Display LinkedIn URL as a clickable link"""
        if obj.metadata and 'linkedin_url' in obj.metadata:
            url = obj.metadata['linkedin_url']
            return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-yes.svg" alt="LinkedIn" style="height: 15px; width: 15px;"/> LinkedIn</a>', url)
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="No LinkedIn" style="height: 15px; width: 15px;"/> No LinkedIn')
    linkedin_url.short_description = 'LinkedIn'

    def has_outreach(self, obj):
        return obj.outreach_emails.exists()
    has_outreach.boolean = True
    has_outreach.short_description = "Has Outreach"

    def company_size_display(self, obj):
        if not obj.company_size:
            return '-'
        return obj.company_size
    company_size_display.short_description = 'Company Size'

    def funding_display(self, obj):
        if not obj.funding_amount:
            return '-'
        amount = float(obj.funding_amount)
        if amount >= 1_000_000_000:
            return f'${amount/1_000_000_000:.1f}B'
        elif amount >= 1_000_000:
            return f'${amount/1_000_000:.1f}M'
        else:
            return f'${amount:,.0f}'
    funding_display.short_description = 'Funding'

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

    def generate_messages_view(self, request, lead_id):
        lead = Lead.objects.get(id=lead_id)
        client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Build detailed company profile
        company_profile = {
            'name': lead.company,
            'industry': lead.industry,
            'contact_name': lead.name,
            'position': lead.position,
            'achievements': []
        }
        
        # Add funding details if available
        if lead.funding_amount:
            amount = float(lead.funding_amount)
            if amount >= 1_000_000_000:
                company_profile['achievements'].append(
                    f"secured ${amount/1_000_000_000:.1f}B in funding"
                )
            elif amount >= 1_000_000:
                company_profile['achievements'].append(
                    f"raised ${amount/1_000_000:.1f}M"
                )
        
        # Add growth indicators
        if lead.open_positions:
            company_profile['achievements'].append(
                f"actively expanding with {lead.open_positions} open positions"
            )
        
        # Add company size context
        if lead.company_size:
            company_profile['size_context'] = f"a {lead.company_size} company in the {lead.industry} space"
        else:
            company_profile['size_context'] = f"a company making waves in the {lead.industry} space"
        
        # Format achievements for email
        achievements_text = ""
        if company_profile['achievements']:
            achievements_text = " and " + ", ".join(company_profile['achievements'])
        
        # Generate email content
        email_prompt = f"""Generate a personalized email following this exact structure but with natural language:

Hi {{name}},

I came across {company_profile['name']}'s work in the {company_profile['industry']} sector. As {company_profile['size_context']}{achievements_text}, your innovations caught my attention.

Your role as {company_profile['position']} particularly interests me, and I'd love to schedule a quick call to learn more about your work and discuss potential synergies.

Would you have 15 minutes this week for a brief chat?

Best regards,
[Your name]

REQUIREMENTS:
1. Use the company details provided but make it sound natural and conversational
2. Keep the same brief, friendly tone as the template
3. Maintain the 4-part structure: opening, observation, interest, call to action
4. Reference their specific achievements naturally in the conversation
5. Keep it concise and focused on learning about their company
"""
        
        # Generate LinkedIn message
        linkedin_prompt = f"""Generate a personalized LinkedIn connection message following this exact structure:

Hi {company_profile['contact_name']},

I came across {company_profile['name']}'s innovative work in {company_profile['industry']}. {company_profile['size_context']}{achievements_text}. Would love to connect and learn more about your work as {company_profile['position']}.

REQUIREMENTS:
1. Use this exact information but make it sound natural:
   - Company: {company_profile['name']}
   - Industry: {company_profile['industry']}
   - Role: {company_profile['position']}
   - Size: {company_profile['size_context']}
   - Achievement: {company_profile['achievements'][0] if company_profile['achievements'] else 'growth in the industry'}
2. Must be under 300 characters
3. Keep the same friendly, professional tone
4. Show specific knowledge of their company
5. Focus on genuine interest in their work
6. End with connecting to learn more
7. Do not mention selling or services
"""
        
        try:
            # Generate email content
            email_completion = client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": email_prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Generate LinkedIn message
            linkedin_completion = client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": linkedin_prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=300,
            )
            
            email_content = email_completion.choices[0].message.content.strip()
            linkedin_content = linkedin_completion.choices[0].message.content.strip()
            
            # Save both messages
            Outreach.objects.create(
                lead=lead,
                email_content=email_content,
                linkedin_content=linkedin_content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Messages generated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@admin.register(Outreach)
class OutreachAdmin(admin.ModelAdmin):
    list_display = ('lead_company', 'lead_name', 'generated_at', 'email_status', 'linkedin_status', 'message_previews')
    list_filter = ('is_approved', 'is_linkedin_approved', 'generated_at')
    search_fields = ('lead__company', 'lead__name', 'email_content', 'linkedin_content')
    readonly_fields = ('generated_at', 'lead_link', 'email_content', 'linkedin_content')
    
    fieldsets = (
        ('Lead Information', {
            'fields': ('lead_link', 'generated_at')
        }),
        ('Email Message', {
            'fields': ('email_content', 'is_approved')
        }),
        ('LinkedIn Message', {
            'fields': ('linkedin_content', 'is_linkedin_approved')
        })
    )
    
    def lead_company(self, obj):
        return obj.lead.company if obj.lead else 'Unknown'
    lead_company.short_description = 'Company'
    
    def lead_name(self, obj):
        return obj.lead.name if obj.lead else 'Unknown'
    lead_name.short_description = 'Contact Name'
    
    def lead_link(self, obj):
        if obj.lead:
            url = reverse('admin:api_lead_change', args=[obj.lead.id])
            return format_html('<a href="{}">{}</a>', url, obj.lead.name)
        return 'Unknown'
    lead_link.short_description = 'Lead'
    
    def email_status(self, obj):
        return format_html(
            '<img src="/static/admin/img/icon-{}.svg" alt="{}" title="{}" style="height: 15px; width: 15px;"/>',
            'yes' if obj.is_approved else 'no',
            'Approved' if obj.is_approved else 'Not Approved',
            'Email Approved' if obj.is_approved else 'Email Not Approved'
        )
    email_status.short_description = 'Email Status'

    def linkedin_status(self, obj):
        return format_html(
            '<img src="/static/admin/img/icon-{}.svg" alt="{}" title="{}" style="height: 15px; width: 15px;"/>',
            'yes' if obj.is_linkedin_approved else 'no',
            'Approved' if obj.is_linkedin_approved else 'Not Approved',
            'LinkedIn Message Approved' if obj.is_linkedin_approved else 'LinkedIn Message Not Approved'
        )
    linkedin_status.short_description = 'LinkedIn Status'
    
    def message_previews(self, obj):
        email_preview = obj.email_content[:100] + '...' if len(obj.email_content) > 100 else obj.email_content
        linkedin_preview = obj.linkedin_content[:100] + '...' if len(obj.linkedin_content) > 100 else obj.linkedin_content
        return format_html(
            '<strong>Email:</strong><br>{}<br><br><strong>LinkedIn:</strong><br>{}',
            email_preview,
            linkedin_preview
        )
    message_previews.short_description = 'Message Previews'

@admin.register(LeadMessage)
class LeadMessageAdmin(admin.ModelAdmin):
    list_display = ('lead', 'created_at', 'message_preview')
    list_filter = ('created_at',)
    search_fields = ('lead__name', 'lead__company', 'linkedin_message', 'email_content')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.linkedin_message[:100] + '...' if len(obj.linkedin_message) > 100 else obj.linkedin_message
    message_preview.short_description = 'LinkedIn Message Preview'
