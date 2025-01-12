# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
import pandas as pd
from django.http import HttpResponse
from django.db.models import Count, Q
from vaultapp.models import PublicLetter,LetterReaction,Comment, BlogPost, BlogInteraction
from django.db import models
from django.shortcuts import render, redirect
from vaultapp.form import LetterForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404



def letter_scheduled(request):
    return render(request, 'vaultapp/letter_scheduled.html')

def letter_scheduled(request):
    return render(request, 'vaultapp/letter_scheduled.html')

def write_letter(request):
    # Fetch the latest 6 blog posts to display
    blogs = BlogPost.objects.all().order_by('-created_at')[:6]

    # Handle form submission
    if request.method == 'POST':
        form = LetterForm(request.POST)
        
        if form.is_valid():
            letter = form.save(commit=False)  # Don't save to DB yet

            # Check if user is authenticated
            if request.user.is_authenticated:
                letter.user = request.user  # Associate the letter with the logged-in user
            else:
                # If the user is not logged in, inform them and redirect to login
                messages.info(request, "You need to log in before sending the letter.")
                return redirect('signin1')  # Redirect to your login view (replace 'login' with your actual URL name)
            
            letter.status = 'scheduled'  # Set status to scheduled by default
            letter.save()

            messages.success(request, "Your letter has been scheduled successfully.")
            return redirect('letter_scheduled')  # Redirect to a confirmation page after scheduling
        else:
            # If form is invalid, display an error message
            messages.error(request, "There was an error with your submission.")
    else:
        form = LetterForm()

    return render(request, 'vaultapp/write_letter.html', {'form': form, 'blogs': blogs})



def blog_interaction(request, public_letter_id):
    public_letter = PublicLetter.objects.get(id=public_letter_id)

    if request.user.is_authenticated:
        # For authenticated users, assign their User instance
        interaction = BlogInteraction.objects.create(
            public_letter=public_letter,
            user=request.user,  # Assign the authenticated user
            interaction_type=request.POST.get('interaction_type')  # e.g., 'view'
        )
    else:
        # For unauthenticated (anonymous) users, do not assign user, instead use session_id
        interaction = BlogInteraction.objects.create(
            public_letter=public_letter,
            session_id=request.session.session_key,  # Use session_id to track anonymous user
            interaction_type=request.POST.get('interaction_type')  # e.g., 'view'
        )
    
    return HttpResponse("Interaction created.")


def blog_detail(request, id):
    try:
        blog = BlogPost.objects.get(id=id)
    except BlogPost.DoesNotExist:
        return redirect('error_page')  # Handle the case where the blog does not exist
    return render(request, 'vaultapp/blog_detail.html', {'blog': blog})




def home(request):
    # Fetching trending posts (most shared, unpublished, limited to 6)
    trending_posts = PublicLetter.objects.filter(is_published=True).order_by('-shared_date')[6:]
    
    # Fetching latest posts (most recent, unpublished, limited to 10)
    latest_posts = PublicLetter.objects.filter(is_published=True).order_by('-shared_date')[10:]
    
    # Rendering the home page with both sets of posts
    return render(request, 'vaultapp/home.html', {
        'trending_posts': trending_posts,
        'latest_posts': latest_posts
    })


def about(request):
    return render(request,'vaultapp/about.html')

def post_list(request):
    posts = PublicLetter.objects.filter(is_published= True)
    return render(request, 'vaultapp/post.html', {'object_list': posts})


def post_detail(request, id):
    post = PublicLetter.objects.get(id=id)
    comments = Comment.objects.filter(public_letter=post, parent_comment__isnull=True).prefetch_related('replies')
    if not request.session.get(f'viewed_post_{id}', False):
        if request.user.is_authenticated:
            # For authenticated users
            BlogInteraction.objects.create(
                public_letter=post,
                user=request.user,  # Assign the authenticated user
                interaction_type='view'
            )
        else:
            # For unauthenticated (anonymous) users
            BlogInteraction.objects.create(
                public_letter=post,
                session_id=request.session.session_key,  # Track anonymous users with session_id
                interaction_type='view'
            )
        # Mark the post as viewed in the session
        request.session[f'viewed_post_{id}'] = True

    # Increment the view count for the post
    post.view_count += 1
    post.save()
    # like_count = LetterReaction.objects.filter(public_letter=post).count()

    # Optionally, check if the current user has already reacted
    # user_reacted = LetterReaction.objects.filter(public_letter=post, user=request.user).exists()

    public_letters = PublicLetter.objects.filter(is_published=True).values('id', 'description', 'title')
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

    recommended_blogs2 = post.collaborative_recommend_blogs(top_n=5)


    context = {
        'post': post,
        'comments': comments,
        'recommended_blogs': recommended_blogs,
        'recommended_blogs2': recommended_blogs2,
        # 'like_count': like_count,
        # 'user_reacted': user_reacted
    }
    return render(request, 'vaultapp/post_detail.html', context)


def like_post(request, id):
    if request.method == "POST":
        public_letter = get_object_or_404(PublicLetter, id=id)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            # For authenticated users, handle the like/unlike logic
            reaction, created = LetterReaction.objects.get_or_create(
                public_letter=public_letter,
                user=request.user
            )

            if not created:
                # If the reaction already exists, remove it (unlike)
                reaction.delete()
                liked = False
            else:
                # If no reaction existed, create it (like)
                liked = True

            # Record the like interaction in BlogInteraction for authenticated users
            BlogInteraction.objects.create(
                public_letter=public_letter,
                user=request.user,
                interaction_type='like'
            )

            # Return updated like count
            like_count = public_letter.likes.count()

            return JsonResponse({
                'liked': liked,
                'like_count': like_count,
            })

        else:
            # If the user is not authenticated, return a message prompting them to login
            return JsonResponse({
                'error': 'You must be logged in to like this post.'
            }, status=401)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_comment(request, id):
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            content = request.POST.get('content')
            parent_comment_id = request.POST.get('parent_comment_id')

            # Validate content
            if not content:
                return render(request, 'vaultapp/post_detail.html', {
                    'error': 'Content cannot be empty',
                    'id': id,
                })

            # Get the public letter
            public_letter = get_object_or_404(PublicLetter, id=id)

            # Get the parent comment (if provided)
            parent_comment = None
            if parent_comment_id:
                parent_comment = Comment.objects.filter(id=parent_comment_id).first()

            # Create the comment
            comment = Comment.objects.create(
                public_letter=public_letter,
                content=content,
                user=request.user,
                parent_comment=parent_comment
            )

            # Record the comment interaction in BlogInteraction for authenticated users
            BlogInteraction.objects.create(
                public_letter=public_letter,
                user=request.user,
                interaction_type='comment',
            )

            # Redirect to the post detail page
            return redirect('post_detail', id=id)

        else:
            # For unauthenticated (anonymous) users, prompt to log in
            return JsonResponse({
                'error': 'You must be logged in to comment on this post.'
            }, status=401)

    return render(request, 'vaultapp/post_detail.html', {'id': id})




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
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

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

