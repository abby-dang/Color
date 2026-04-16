import os
from supabase import create_client, Client

url: str = os.environ.get("https://ytueocpenouaflaqlrlv.supabase.co")
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0dWVvY3Blbm91YWZsYXFscmx2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTcwODA3NiwiZXhwIjoyMDkxMjg0MDc2fQ.5NGYsXz773dSEeWb80WfOun9iXlzEMnXsF58c0n0zEA")
supabase: Client = create_client(url, key)