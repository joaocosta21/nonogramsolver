from django.urls import path
from .views import solve_picross
from .views import home

urlpatterns = [
    path('solve/', solve_picross, name='solve_picross'),
    path('', home, name='home'),
]
