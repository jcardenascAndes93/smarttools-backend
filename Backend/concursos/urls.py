from django.urls import include, path
from django.conf.urls import url
from .views import ListUserConcursosView, HomeConcursoView

urlpatterns = [
    path('list/', ListUserConcursosView.as_view({'get': 'list'}), name='list_concursos'),
    path('list/<int:pk>', ListUserConcursosView.as_view({'get': 'retrieve'}), name='list_concurso'),
    path('new/', ListUserConcursosView.as_view({'post': 'create'}), name='create_concursos'),
    path('update/<int:pk>', ListUserConcursosView.as_view({'patch': 'partial_update'}), name='update_concurso'),
    path('delete/<int:pk>', ListUserConcursosView.as_view({'post': 'destroy'}), name='delete_concurso'),    
    path('<str:concurso_url>/', HomeConcursoView.as_view({'get': 'retrieve'}), name='home_videos_list'),
    path('<str:concurso_url>/upload_video', HomeConcursoView.as_view({'post': 'create'}), name='create_video'),
]