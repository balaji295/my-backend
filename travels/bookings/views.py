#authicate,permisions,token,status,respomce,generics,Apiviews
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status,generics
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, BusSerializer, BookingSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status 
from.models import Bus,Seat,Bookings
from django.views.decorators.csrf import csrf_exempt


class RegisterView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self,request):
        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            token,created=Token.objects.get_or_create (user = user)

            return Response({'token':token.key},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    'token': token.key,
                    'user_id': user.id
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Invalid Credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

class BusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

class BookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        seat_id = request.data.get('seat')
        try:
            seat = Seat.objects.get(id=seat_id)
            if seat.is_booked:
                return Response({'error': 'Seat already booked'}, status=status.HTTP_400_BAD_REQUEST)
            seat.is_booked = True
            seat.save()
            
            booking = Bookings.objects.create(
                user=request.user,
                seat=seat,
            )
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Seat.DoesNotExist:
            return Response({'error': 'Invalid SEAT ID'}, status=status.HTTP_400_BAD_REQUEST)


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request):
        seat_ids = request.data.get('seats', [])
        bus_id = request.data.get('bus_id')

        if not seat_ids:
            return Response({"error": "No seats provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not bus_id:
            return Response({"error": "Bus ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        booked_seats = []

        for seat_id in seat_ids:
            seat = Seat.objects.filter(seat_number=seat_id, bus_id=bus_id).first()

            if not seat:
                return Response({"error": f"Seat {seat_id} not found in this bus"}, status=status.HTTP_404_NOT_FOUND)

            if seat.is_booked:
                return Response({"error": f"Seat {seat.seat_number} is already booked"}, status=status.HTTP_400_BAD_REQUEST)

            booking = Bookings.objects.create(
                user=request.user,
                seat=seat,
                bus_id=bus_id 
            )

            seat.is_booked = True
            seat.save()
            booked_seats.append(booking.id)

        return Response({"message": "Booking successful", "booking_ids": booked_seats}, status=status.HTTP_201_CREATED)


class UserBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != int(user_id):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        bookings = Bookings.objects.filter(user_id=user_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)