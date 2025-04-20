import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import your_app_name.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'major__project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            datacleaning.routing.websocket_urlpatterns
        )
    ),
})
