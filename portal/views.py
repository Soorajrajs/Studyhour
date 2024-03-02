from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests 
import wikipedia
from wikipedia.exceptions import DisambiguationError
from .models  import *
from django.contrib.auth import logout
from django.contrib.auth.decorators  import login_required
# Create your views here.
def home(request):
    return render(request,'portal/home.html')

@login_required()
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
# @login_required()
class NoteDetailView(generic.DetailView):
    model=Notes

@login_required()
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
    print(homework)
    print("Len of homework is",len(homework))
    context={
        'homeworks':homework,
        'homewoks_done':homework_done,
        'form':form  }
    return render(request,'portal/homework.html',context)

@login_required()
def update_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    print(homework)
    if homework.is_finished == True:
        homework.is_finished =  False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')

@login_required()
def delete_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    homework.delete()
    messages.warning(request,"Homework Deleted Successfully!")
    return redirect('homework')

@login_required()
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

@login_required()
def todo(request):
    if request.method=="POST":
        form=TodoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['status']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished=False
            todo=Todo(user=request.user,title=request.POST['title'],status=finished)
            todo.save()
            messages.success(request,"Task added successfully")
            return redirect('todo')
    else:
        form=TodoForm()
   
    todo=Todo.objects.all()
    if len(todo)==0:
        todo_done=True
    else:
        todo_done=False
    context= {'form':form, 'todos':todo,'todos_done':todo_done}
    return render(request,'portal/todo.html',context)

@login_required()
def update_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    print(todo)
    if todo.status == True:
        todo.status =  False
    else:
        todo.status=True
    todo.save()
    return redirect('todo')

@login_required()
def delete_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    todo.delete()
    messages.warning(request,"Task deleted Successfully")
    return redirect('todo')

@login_required()
def books(request):
    if request.method == 'POST':
        form=DashboardForm(request.POST)
        text=request.POST['text']
        url="https://www.googleapis.com/books/v1/volumes?q="+text
        r=requests.get(url)
        answer=r.json()
        result_list=[]
        for i in range(10):
            result_dict={
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'category':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
        
            result_list.append(result_dict)
            context={
                "form":form,
                'results':result_list
            }
        print(context)
        return render(request,'portal/books.html',context)

    else:
        form=DashboardForm()
    context={'form':form}
    return render(request,'portal/books.html',context)

@login_required()
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text', '')  # Using cleaned_data to get the validated text
            url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + text
            try:
                r = requests.get(url)
                r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                answer = r.json()

                if isinstance(answer, list) and answer:
                    data = answer[0]

                    # Extract phonetics information
                    if 'phonetics' in data:
                        phonetics = data.get('phonetics', [{'text': 'No phonetics available'}])[0].get('text')

                        # phonetics = data['phonetics'][0]['text'] if data['phonetics'] else "No phonetics available"
                    else:
                        phonetics = "No phonetics available"

                    # Extract meanings information
                    if 'meanings' in data:
                        meanings = data['meanings']
                        if meanings:
                            definition = meanings[0]['definitions'][0]['definition'] if meanings[0]['definitions'] else "No definition available"
                            example = meanings[0]['definitions'][0].get('example', "No example available")
                            synonyms = meanings[0]['definitions'][0].get('synonyms', [])
                        else:
                            definition = "No definition available"
                            example = "No example available"
                            synonyms = []
                    else:
                        definition = "No definition available"
                        example = "No example available"
                        synonyms = []

                    context = {
                        "form": form,
                        'input': text,
                        'phonetics': phonetics,
                        'definition': definition,
                        'example': example,
                        'synonyms': synonyms
                    }
                    return render(request, 'portal/dictionary.html', context)
                else:
                    context = {"form": form, 'error_message': 'Invalid API response'}
            except requests.RequestException as e:
                print("Request Exception:", e)
                context = {"form": form, 'error_message': 'Failed to fetch data from the API'}
        else:
            context = {"form": form}
    else:
        form = DashboardForm()
        context = {"form": form}
    
    return render(request, 'portal/dictionary.html', context)

@login_required()
def wiki(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                search = wikipedia.page(text)
                context = {
                    'form': form,
                    'title': search.title,
                    'link': search.url,
                    'details': search.summary,
                }
            except DisambiguationError as e:
                options = e.options
                context = {
                    'form': form,
                    'error_message': f"Multiple options found for '{text}': {', '.join(options)}",
                    'options': options,
                }
            except wikipedia.exceptions.PageError:
                context = {
                    'form': form,
                    'error_message': f"No Wikipedia page found for '{text}'.",
                }
            return render(request, 'portal/wiki.html', context)

    else:
        form = DashboardForm()

    context = {'form': form}
    return render(request, 'portal/wiki.html', context)

@login_required()
def conversion(request):
    if  request.method == "POST":
        form=ConversionForm(request.POST)
        if request.POST['measurement']=='length':
            measurement_form=ConversionLengthForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='yard' and second=='foot':
                        answer=f'{input}yard={int(input)*3} foot'
                    if first=='foot' and second=='yard':
                        answer=f'{input}foot={int(input)/3} yard'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
        if request.POST['measurement']=='mass':
            measurement_form=ConversionMassForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='pound' and second=='kilogram':
                        answer=f'{input} pound={int(input)*0.453592} kilogram'
                    if first=='kilogram' and second=='pound':
                        answer=f'{input} kilogram={int(input)*2.20462} pound'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
    else:
        form=ConversionForm()
        context={'form':form,
                'input':False}
    return render(request, "portal/conversion.html",context)

@login_required()
def register(request):
    if  request.method=="POST":
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request,f'Account Created successfully for {username}')
            return redirect('login')
    else:
        form =UserRegistrationForm()
    context={
        'form':form}
    return  render(request,"portal/register.html",context)

@login_required()
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(status=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todo_done=True
    else:
        todo_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todo_done':todo_done
    }
    return render(request, "portal/profile.html",context)

@login_required()
def custom_logout(request):
    logout(request)
    # Redirect to a specific page after logout, or any desired URL
    return redirect('login')
