from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # api/urlsm.py를 포함

    re_path(r"^(?P<path>.*)$", TemplateView.as_view(template_name='index.html'), name='home'),  # 여기서 index.html 사용
]

#if settings.DEBUG:  # DEBUG 모드에서 미디어 파일 서빙
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)