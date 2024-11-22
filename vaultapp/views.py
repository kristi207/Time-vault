from django.shortcuts import render
from vaultapp.models import PublicLetter

def home(request):
    return render(request, 'vaultapp/home.html')

def trending_posts(request):
    # Fetch the posts you want to display (e.g., the latest 4 posts)
    posts = PublicLetter.objects.all()[:6]  # Adjust this to your query needs
    return render(request, 'your_template.html', {'posts': posts})

def about(request):
    return render(request,'vaultapp/about.html')

def post_list(request):
    posts = PublicLetter.objects.filter(is_published= False)
    return render(request, 'vaultapp/post.html', {'object_list': posts})


def post_detail(request, id):
    post = PublicLetter.objects.get(id=id)
    return render(request, 'vaultapp/post_detail.html', {'post': post})

def signup(request):
    if request.method == 'POST':
        # Process form data (handle the signup process)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Here you can create a user or handle the signup logic
        print(f"Received Signup - Name: {name}, Email: {email}, Password: {password}")

        # Redirect to a success page (or homepage, or wherever you want)
      

    return render(request, 'signup.html')  # Render the signup form
