from .views import MediaView,CeleryTestView,TaskStatusView,ProcessVideo
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', MediaView.as_view(), name='video-upload'),
    path("test-celery/", CeleryTestView.as_view(), name="test-celery"),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path("celery-video/",ProcessVideo.as_view(), name="process-video-with-celery")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)