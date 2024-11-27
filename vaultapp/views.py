from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from vaultapp.models import PublicLetter,LetterReaction,Comment
from django.db import models


def home(request):
    return render(request, 'vaultapp/home.html')

def trending_posts(request):
    posts = PublicLetter.objects.all()[:6]  
    return render(request, 'your_template.html', {'posts': posts})

def latest_posts(request):
    posts = PublicLetter.objects.all()[:6]  
    return render(request, 'your_template.html', {'latest_posts': posts})

def about(request):
    return render(request,'vaultapp/about.html')

def post_list(request):
    posts = PublicLetter.objects.filter(is_published= False)
    return render(request, 'vaultapp/post.html', {'object_list': posts})


def post_detail(request, id):
    post = PublicLetter.objects.get(id=id)
    reactions = LetterReaction.objects.filter(public_letter=post).values('reaction_type').annotate(count=models.Count('reaction_type'))
    comments = Comment.objects.filter(public_letter=post, parent_comment__isnull=True).prefetch_related('replies')
    recommended_blogs = PublicLetter.objects.filter(is_published=False).exclude(id=id)[:5]  # Fetch 5 recommended blogs

    context = {
        'post': post,
        'reactions': {reaction['reaction_type']: reaction['count'] for reaction in reactions},
        'comments': comments,
        'recommended_blogs': recommended_blogs,
    }
    return render(request, 'vaultapp/post_detail.html', context)

def add_reaction(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        reaction_type = request.POST.get('REACTION_CHOICES')
        public_letter = PublicLetter.objects.get(PublicLetter, id=id)
        LetterReaction.objects.create(public_letter=public_letter, reaction_type=reaction_type, user=request.user)
    return render('vaultapp/post_detail.html', id=id)

def add_comment(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        parent_comment_id = request.POST.get('parent_comment_id')
        public_letter = PublicLetter.objects.get(PublicLetter, id=id)
        parent_comment = Comment.objects.filter(id=parent_comment_id).first()
        Comment.objects.create(public_letter=public_letter, content=content, user=request.user, parent_comment=parent_comment)
    return render('vaultapp/post_detail.html', id=id)
#signup
def signup(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Password validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'vaultapp/signup.html')
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'vaultapp/signup.html')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'vaultapp/signup.html')

        # Create the user
        user = User.objects.create_user(username=name, email=email, password=password)
        user.save()

        # Automatically log the user in
        login(request, user)

        messages.success(request, "Account created successfully! You are now logged in.")
        return redirect('home')  # Redirect to the homepage or dashboard

    return render(request, 'vaultapp/signup.html')

#signin
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Login the user
            login(request, user)

            # Show success message
            messages.success(request, "Logged in successfully!")

            # Redirect to the home page or dashboard
            return redirect('home')  # Replace 'home' with your desired URL name
        else:
            # Invalid credentials
            messages.error(request, "Invalid email or password.")
            return render(request, 'vaultapp/signin.html')

    return render(request, 'vaultapp/signin.html')