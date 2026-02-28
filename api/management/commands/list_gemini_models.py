import os
import google.generativeai as genai
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Lists all available Gemini models for the configured API key that support content generation.'

    def handle(self, *args, **options):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR("GEMINI_API_KEY environment variable not found."))
            return

        try:
            genai.configure(api_key=api_key)
            self.stdout.write(self.style.SUCCESS("Available models for content generation:"))
            
            count = 0
            for model in genai.list_models():
                # We only care about models that can be used for chat/text generation
                if 'generateContent' in model.supported_generation_methods:
                    self.stdout.write(f"- {model.name}")
                    count += 1
            
            if count == 0:
                self.stdout.write(self.style.WARNING("No models supporting 'generateContent' found."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while trying to list models: {e}"))
