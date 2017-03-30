from django.conf.urls import url

from . import views

app_name = 'proto1'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^run_emotion_recog', views.run_emotion_recog, name='run_emotion_recog'),
    url(r'^get_video_results', views.get_video_results, name='get_video_results'),
]
