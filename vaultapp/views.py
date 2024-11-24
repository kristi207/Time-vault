from django.shortcuts import render
from vaultapp.models import PublicLetter,LetterReaction,Comment

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
    reactions = LetterReaction.objects.filter(public_letter=post).values('reaction_type').annotate(count=models.Count('reaction_type'))
    comments = Comment.objects.filter(public_letter=post, parent_comment__isnull=True).prefetch_related('replies')
    recommended_blogs = PublicLetter.objects.filter(is_published=True).exclude(id=id)[:5]  # Fetch 5 recommended blogs

    context = {
        'post': post,
        'reactions': {reaction['reaction_type']: reaction['count'] for reaction in reactions},
        'comments': comments,
        'recommended_blogs': recommended_blogs,
    }
    return render(request, 'post_detail.html', context)

def add_reaction(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        reaction_type = request.POST.get('REACTION_CHOICES')
        public_letter = PublicLetter.objects.get(PublicLetter, id=id)
        LetterReaction.objects.create(public_letter=public_letter, reaction_type=reaction_type, user=request.user)
    return render('post_detail', id=id)

def add_comment(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        parent_comment_id = request.POST.get('parent_comment_id')
        public_letter = PublicLetter.objects.get(PublicLetter, id=id)
        parent_comment = Comment.objects.filter(pk=parent_comment_id).first()
        Comment.objects.create(public_letter=public_letter, content=content, user=request.user, parent_comment=parent_comment)
    return render('post_detail', id=id)

def signup(request):
    if request.method == 'POST':
        # Process form data (handle the signup process)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Here you can create a user or handle the signup logic
        print(f"Received Signup - Name: {name}, Email: {email}, Password: {password}")

        # Redirect to a success page (or homepage, or wherever you want)
      

    return render(request, 'vaultapp/signup.html')  # Render the signup form

def signin(request):
    if request.method == 'POST':
        # Process form data (handle the signup process)
       
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Here you can create a user or handle the signup logic
        print(f"Received Signup -  Email: {email}, Password: {password}")

        # Redirect to a success page (or homepage, or wherever you want)
      

    return render(request, 'vaultapp/signin.html')  # Render the signup form