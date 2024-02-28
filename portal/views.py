from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch

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

def delete_note(request,pk):
    Notes.objects.get(id=pk).delete()
    messages.warning(request,"Notes Deleted Successfully!")
    return redirect('notes')

class NoteDetailView(generic.DetailView):
    model=Notes

def homework(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished=False
            homeworks=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished)
            homeworks.save()
            messages.success(request,"Homework Added Successfully!")
    else:
        form=HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    context={
        'homeworks':homework,
        'homewoks_done':homework_done,
        'form':form  }
    return render(request,'portal/homework.html',context)

def update_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    print(homework)
    if homework.is_finished == True:
        homework.is_finished =  False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')

def delete_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    homework.delete()
    messages.warning(request,"Homework Deleted Successfully!")
    return redirect('homework')

def youtube(request):
    if request.method == 'POST':
        form=DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=15)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc=''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc=desc+j['text']
                result_dict['description']=desc
                result_list.append(result_dict)
                context={
                    "form":form,
                    'results':result_list
                }
        print(context)
        return render(request,'portal/youtube.html',context)

    else:
        form=DashboardForm()
    context={'form':form}
    return render(request,'portal/youtube.html',context)
