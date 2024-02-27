from django.shortcuts import render
from django.contrib import messages
from .forms import *

# Create your views here.
def home(request):
    return render(request,'portal/home.html')

def notes(request):
    if  request.method == 'POST':
        form=NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes added successfully")
    else:
        form = NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes, 'form':form}
    return render(request,'portal/notes.html',context)