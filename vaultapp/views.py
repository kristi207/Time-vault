from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
import pandas as pd
from vaultapp.models import PublicLetter,LetterReaction,Comment, BlogPost
from django.db import models
from django.shortcuts import render, redirect
from vaultapp.form import LetterForm
from .models import Letter
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from vaultapp.form import LetterForm
from vaultapp.models import BlogPost

def write_letter(request):
    # Fetch the latest 6 blog posts
    blogs = BlogPost.objects.all().order_by('-created_at')[:6]

    if request.method == 'POST':
        form = LetterForm(request.POST)
        if form.is_valid():
            # Save the letter
            letter = form.save(commit=False)
            if request.user.is_authenticated:
                letter.user = request.user  # Associate the letter with the logged-in user
            letter.status = 'scheduled'  # Set status to scheduled by default
            letter.save()

            messages.success(request, "Your letter has been scheduled successfully.")
            return redirect('vaultapp/letter_scheduled')  # Redirect to a confirmation page
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = LetterForm()

    return render(request, 'vaultapp/write_letter.html', {'form': form, 'blogs': blogs})


# def write_letter(request):
#     if request.method == 'POST':
#         form = LetterForm(request.POST)
#         if form.is_valid():
#             # Save the letter
#             letter = form.save(commit=False)
#             if request.user.is_authenticated:
#                 letter.user = request.user  # Associate the letter with the logged-in user
#             letter.status = 'scheduled'  # Set status to scheduled by default
#             letter.save()

#             messages.success(request, "Your letter has been scheduled successfully.")
#             return redirect('vaultapp/letter_scheduled')  # Redirect to a confirmation page
#         else:
#             messages.error(request, "There was an error with your submission.")
#     else:
#         form = LetterForm()
#     return render(request, 'vaultapp/write_letter.html', {'form': form})

def letter_scheduled(request):
    return render(request, 'vaultapp/letter_scheduled.html')


# def write_letter(request): 
#     blogs = BlogPost.objects.all().order_by('-created_at')[:6]  # Fetch the latest 6 blogs
#     return render(request, 'vaultapp/write_letter.html', {'blogs': blogs})

def blog_detail(request, id):
    try:
        blog = BlogPost.objects.get(id=id)
    except BlogPost.DoesNotExist:
        return redirect('error_page')  # Handle the case where the blog does not exist
    return render(request, 'vaultapp/blog_detail.html', {'blog': blog})


def home(request):
    return render(request, 'vaultapp/home.html')

def home(request):
    # Fetching trending posts (most shared, unpublished, limited to 6)
    trending_posts = PublicLetter.objects.filter(is_published=False).order_by('-shared_date')[:6]
    
    # Fetching latest posts (most recent, unpublished, limited to 10)
    latest_posts = PublicLetter.objects.filter(is_published=False).order_by('-shared_date')[:10]
    
    # Rendering the home page with both sets of posts
    return render(request, 'vaultapp/home.html', {
        'trending_posts': trending_posts,
        'latest_posts': latest_posts
    })


def about(request):
    return render(request,'vaultapp/about.html')

def post_list(request):
    posts = PublicLetter.objects.filter(is_published= False)
    return render(request, 'vaultapp/post.html', {'object_list': posts})


def post_detail(request, id):
    post = PublicLetter.objects.get(id=id)
    reactions = (
        LetterReaction.objects.filter(public_letter=post)
        .values('reaction_type')
        .annotate(count=models.Count('reaction_type'))
    )   
    comments = Comment.objects.filter(public_letter=post, parent_comment__isnull=True).prefetch_related('replies')
    
    public_letters = PublicLetter.objects.filter(is_published=False).values('id', 'description', 'title')
    df = pd.DataFrame(public_letters)
    df['description'] = df['description'].fillna('')  # Handle empty descriptions

    # Apply the recommendation system
    custom_tfidf = PublicLetter.recommend_blogs()  # Reuse the recommendation method from the model

    # Extract recommendations for the current post
    recommendations = next(
        (rec['recommended_blogs'] for rec in custom_tfidf if rec['id'] == post.id),
        []
    )
    
    # Fetch recommended blog objects from IDs
    recommended_blogs = PublicLetter.objects.filter(id__in=[rec['id'] for rec in recommendations])

    recommended_blogs2 = PublicLetter.objects.filter(is_published=False).exclude(id=id)[:5]  # Fetch 5 recommended blogs
    print("Recommendations:", recommendations)

    context = {
        'post': post,
        'reactions': {reaction['reaction_type']: reaction['count'] for reaction in reactions},
        'comments': comments,
        'recommended_blogs': recommended_blogs,
        'recommended_blogs2': recommended_blogs2,
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