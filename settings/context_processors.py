from .services import SiteService


def site_settings(request):
    return {
        'site_settings': SiteService.settings()
    }

# Register it
# Now every template has site_settings available