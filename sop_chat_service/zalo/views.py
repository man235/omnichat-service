from django.shortcuts import render

# Create your views here.
def room(request, room_id):
    context = {}
    return render(request, 'zalo/room.html', context)