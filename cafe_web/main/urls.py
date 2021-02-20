from django.conf.urls.static import static

from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path("", mainpage, name="mainpage"),
    path('cafedetail/<int:pk>/',cafedetail,name='cafedetail'),
    path('reviewdetail/<int:pk>/',reviewdetail,name='reviewdetail'),
    path("cafe_csv_upload", cafe_csv_upload, name="cafe_csv_upload"),
    path("csv_upload", csv_upload, name="csv_upload"),
    path("write_recommend",write_recommend,name="write_recommend"),
]
