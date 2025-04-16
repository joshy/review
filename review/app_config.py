import os
from dotenv import load_dotenv
from cachelib.file import FileSystemCache

load_dotenv()

# Session settings
SESSION_TYPE = "cachelib"
SESSION_SERIALIZATION_FORMAT = "json"
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="sessions")


# In production, your setup may use multiple web servers behind a load balancer,
# and the subsequent requests may not be routed to the same web server.
# In that case, you may either use a centralized database-backed session store,
# or configure your load balancer to route subsequent requests to the same web server
# by using sticky sessions also known as affinity cookie.
# [1] https://www.imperva.com/learn/availability/sticky-session-persistence-and-cookies/
# [2] https://azure.github.io/AppService/2016/05/16/Disable-Session-affinity-cookie-(ARR-cookie)-for-Azure-web-apps.html
# [3] https://learn.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal#configure-general-settings

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{os.getenv('TENANT_ID', 'common')}"
REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# This resource requires no admin consent
ENDPOINT = "https://graph.microsoft.com/v1.0/users"
SCOPE = ["User.ReadBasic.All"]
