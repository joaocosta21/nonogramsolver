from django.urls import path
from .views import solve_picross

urlpatterns = [
    path('solve/', solve_picross, name='solve_picross'),
]
