# icecream_qr/urls.py


from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/panel/login/', permanent=False)),
    path('', include('qr_ordering.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
