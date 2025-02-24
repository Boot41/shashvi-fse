from django.core.management.base import BaseCommand
from api.models import Lead
from api.scoring import LeadScorer
import pandas as pd
import json

class Command(BaseCommand):
    help = 'Update lead scores based on company data from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file with company data')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # Initialize scorer
        scorer = LeadScorer(target_industry="SaaS")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Process each row
            for index, row in df.iterrows():
                company_data = {
                    'company_name': row.get('company_name'),
                    'funding_amount': row.get('funding_amount'),
                    'industry': row.get('industry'),
                    'hiring_data': {
                        'open_positions': row.get('open_positions', 0)
                    }
                }
                
                # Calculate score
                score = scorer.calculate_total_score(company_data)
                
                # Update lead in database
                leads = Lead.objects.filter(company__iexact=company_data['company_name'])
                if leads.exists():
                    lead = leads.first()
                    lead.lead_score = score
                    lead.metadata = json.dumps({
                        'funding_amount': float(company_data['funding_amount']) if pd.notna(company_data['funding_amount']) else None,
                        'industry': company_data['industry'] if pd.notna(company_data['industry']) else None,
                        'open_positions': company_data['hiring_data']['open_positions']
                    })
                    lead.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated score for {company_data['company_name']}: {score}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No lead found for company: {company_data['company_name']}"
                        )
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error processing CSV: {str(e)}")
            )
