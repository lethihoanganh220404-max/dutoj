from django.urls import path

from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.bang_dieu_khien, name='bang'),
    path('upload/', views.upload_image, name='upload'),
    path('goi-y/<str:ma_bai>/', views.xem_goi_y, name='goi_y'),
    path('sinh-test/<str:ma_bai>/', views.sinh_test, name='sinh_test'),
    path('task/<str:task_id>/', views.trang_thai_task, name='trang_thai_task'),
]
