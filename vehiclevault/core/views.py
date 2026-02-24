from django.shortcuts import render, redirect
from .forms import UsersignupForm
# Create your views here.
def Usersignupview(request):
   if request.method == 'POST':
        form = UsersignupForm(request.POST or None)
        if form.is_valid():
             form.save()
             return redirect('login')  #error here
        else:
             return render(request, 'core/signup.html', {'form': form})
   else:
      form = UsersignupForm()
      return render(request, 'core/signup.html', {'form': form})

def home(request):
    return render(request, 'home.html')