import os
import httpx
from pathlib import Path
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / '.env')

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

#By default every query shares one HTTP/2 connection, which breaks when Django handles
#requests on several threads at once (WinError 10035 / ConnectionTerminated).
#HTTP/1.1 gives each thread its own pooled connection instead.
supabase: Client = create_client(url, key, options=SyncClientOptions(httpx_client=httpx.Client(http2=False)))