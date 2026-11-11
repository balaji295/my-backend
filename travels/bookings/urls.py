
from django.urls import path
from .views import (
    RegisterView, LoginView, BusListCreateView, 
    BusDetailView, CreateBookingView, UserBookingView
)
from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

urlpatterns = [
    path('buses/', BusListCreateView.as_view(), name='buslist'),
    path('buses/<int:pk>/', BusDetailView.as_view(), name='bus_detail'),
    path('register/', RegisterView.as_view(), name='Register'),
    path('login/', LoginView.as_view(), name='register'),
    path('booking/', CreateBookingView.as_view(), name='create_booking'),
    path('user/<int:user_id>/bookings/', UserBookingView.as_view(), name='user_bookings'), 
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]