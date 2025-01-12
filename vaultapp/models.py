from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import numpy as np
from collections import Counter
from django.db.models import Count
import pandas as pd
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db import models
import pandas as pd
import numpy as np
from collections import Counter
from django.db.models.signals import post_save
from django.dispatch import receiver


# Blog Post model for admin to post blogs
class BlogPost(models.Model):
    # Linking to the admin who is posting the blog
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    # Title of the blog
    title = models.CharField(max_length=255)
    # Content of the blog
    content = models.TextField()
    # Blog tags (optional)
    tags = models.CharField(max_length=255, null=True, blank=True)
    # Feature image for the blog (optional)
    feature_image = models.ImageField(upload_to='blog_posts/images/', null=True, blank=True)
    # Published status
    is_published = models.BooleanField(default=False)
    # Date when the blog post was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Date when the blog post was last updated
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Blog Post: {self.title} by {self.author}"

    class Meta:
        ordering = ['-created_at']



# for main letters section
class Letter(models.Model):
    # Linking the letter to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='letters', null=True, blank=True)
    # Email for anonymous or registered users
    recipient_email = models.EmailField()
    # The letter content
    content = models.TextField()
    # The date to send the letter
    send_date = models.DateTimeField()
    # Status of the letter (e.g., scheduled, sent)
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    # Whether the letter is publicly viewable
    is_public = models.BooleanField(default=False)
    # Title for the letter (optional for public readability)
    title = models.CharField(max_length=255, null=True, blank=True)
    # Date when the letter was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Last updated date
    updated_at = models.DateTimeField(auto_now=True)

    def is_future_date(self):
        """Ensure the send date is in the future."""
        return self.send_date > now()

    def __str__(self):
        return f"Letter to {self.recipient_email} scheduled for {self.send_date}"

# read letter section



class PublicLetter(models.Model):
    # Linking to the original letter
    original_letter = models.OneToOneField(
        'Letter', on_delete=models.CASCADE, related_name='public_letter'
    )
    # User who shared the letter publicly
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # A nickname or pseudonym for the public letter
    nickname = models.CharField(max_length=100, null=True, blank=True)
    # Blog-specific fields
    title = models.CharField(max_length=255, null=True, blank=True)  # Blog title
    description = models.TextField(null=True, blank=True)  # Blog description/introduction
    tags = models.CharField(max_length=255, null=True, blank=True)  # Comma-separated tags
    # Feature photo for the public letter/blog
    feature_photo = models.ImageField(upload_to='public_letters/photos/', null=True, blank=True)
    # Date when the letter was made public
    shared_date = models.DateTimeField(auto_now_add=True)
    # Whether the blog is active/published
    is_published = models.BooleanField(default=False)
    # View count
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Public Letter: {self.title or self.original_letter.title or 'The Letter From {self.shared_date}'}"

    @staticmethod
    def recommend_blogs():
        """
        Generate blog recommendations based on the description field using TF-IDF and cosine similarity.
        """
        # Fetch descriptions of published blogs
        public_letters = PublicLetter.objects.filter(is_published=True).values('id', 'description', 'title')
        df = pd.DataFrame(public_letters)
        df['description'] = df['description'].fillna('')  # Handle null descriptions

        # Custom TF-IDF Vectorizer
        class CustomTfidfVectorizer:
            def __init__(self, stopwords=None):
                self.stopwords = stopwords or []
                self.vocabulary_ = None

            def fit_transform(self, documents):
                tokenized_docs = [self._tokenize(doc) for doc in documents]
                all_terms = set(term for doc in tokenized_docs for term in doc)
                self.vocabulary_ = {term: idx for idx, term in enumerate(sorted(all_terms))}
                term_freq_matrix = np.zeros((len(documents), len(self.vocabulary_)))

                for i, doc in enumerate(tokenized_docs):
                    term_counts = Counter(doc)
                    for term, count in term_counts.items():
                        if term in self.vocabulary_:
                            term_freq_matrix[i, self.vocabulary_[term]] = count

                return term_freq_matrix

            def _tokenize(self, document):
                tokens = document.lower().split()
                return [token.strip(".,!?") for token in tokens if token not in self.stopwords]

        # Instantiate the custom TF-IDF vectorizer
        custom_tfidf = CustomTfidfVectorizer(stopwords=["and", "to", "the", "your", "you", "have", "is"])
        tfidf_matrix = custom_tfidf.fit_transform(df['description'])

        # Cosine Similarity Function
        def cosine_similarity(matrix):
            dot_product = np.dot(matrix, matrix.T)
            magnitude = np.linalg.norm(matrix, axis=1)
            denominator = np.outer(magnitude, magnitude)
            denominator[denominator == 0] = 1  # Avoid division by zero
            return dot_product / denominator

        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Recommend Blogs Function
        def recommend_blogs(blog_index, similarity_matrix, df, top_n=5):
            similarity_scores = similarity_matrix[blog_index]
            similar_indices = similarity_scores.argsort()[-(top_n + 1):-1][::-1]  # Exclude the blog itself
            recommended_blogs = df.iloc[similar_indices][['id', 'title', 'description']]
            return recommended_blogs

        # Add Recommendations to DataFrame
        df['recommended_blogs'] = [
            recommend_blogs(idx, similarity_matrix, df).to_dict(orient='records')
            for idx in range(len(df))
        ]

        # Return the dataframe for use in views or APIs
        return df[['id', 'title', 'recommended_blogs']].to_dict(orient='records')
    
    @staticmethod
    def cosine_similarity(matrix):
        dot_product = np.dot(matrix, matrix.T)
        magnitude = np.linalg.norm(matrix, axis=1)
        denominator = np.outer(magnitude, magnitude)
        denominator[denominator == 0] = 1  # Avoid division by zero
        return dot_product / denominator

    def collaborative_recommend_blogs(self, top_n=5):
        """
        Generate blog recommendations for a public letter (blog post) based on collaborative filtering using 
        user interactions and custom cosine similarity. If not enough interactions exist, return the latest top N blogs.
        """
        # Fetch interactions related to the current blog post (public letter)
        interactions = BlogInteraction.objects.filter(public_letter=self)
        interaction_data = interactions.values('user', 'public_letter', 'interaction_type')

        # Check if any interactions exist for the current post
        if not interaction_data:
            print("No interactions found for this blog post.")
            # Fallback: Return the latest top N published blogs (most recent)
            fallback_blogs = PublicLetter.objects.filter(is_published=True).exclude(id=self.id).order_by('-shared_date')[:top_n]
            print(f"Returning fallback blogs: {[blog.title for blog in fallback_blogs]}")
            return fallback_blogs

        # Create a DataFrame from the interaction data
        df = pd.DataFrame(interaction_data)

        # Debugging: Check if the dataframe has any data
        print(f"Interaction DataFrame:\n{df.head()}")

        # Filter out any rows with NaN users (incomplete or invalid interactions)
        df = df.dropna(subset=['user'])

        # Handle case with no or limited interactions
        if df.empty or df.shape[0] < 2:
            print("Not enough interactions to generate meaningful recommendations.")
            # Fallback: Return the latest top N published blogs (most recent)

            fallback_blogs = PublicLetter.objects.filter(is_published=True).exclude(id=self.id) \
                .annotate(comment_count=Count('comment')) \
                .order_by('-comment_count')[:top_n]            
            print(f"Returning fallback blogs: {[blog.title for blog in fallback_blogs]}")
            return fallback_blogs

        # Pivot table to create the user-item interaction matrix
        interaction_matrix = df.pivot_table(
            index='user', 
            columns='public_letter', 
            values='interaction_type', 
            aggfunc=lambda x: 1
        )

        # Debugging: Check if the pivot table is created correctly
        print(f"Interaction Matrix:\n{interaction_matrix.head()}")

        # Replace NaNs with 0 (no interaction)
        interaction_matrix = interaction_matrix.fillna(0)

        # Ensure there are at least two unique blog posts to calculate similarity
        if interaction_matrix.shape[1] < 2:
            print("Not enough blog posts to calculate similarities. Returning fallback blogs.")
            fallback_blogs = PublicLetter.objects.filter(is_published=True).exclude(id=self.id).order_by('-shared_date')[:top_n]
            print(f"Returning fallback blogs: {[blog.title for blog in fallback_blogs]}")
            return fallback_blogs

        # Compute the cosine similarity between users using the custom function
        user_similarity = PublicLetter.cosine_similarity(interaction_matrix.values)

        # Debugging: Check if the cosine similarity matrix is created
        print(f"Cosine Similarity Matrix:\n{user_similarity}")

        # Convert to DataFrame for easier access
        user_similarity_df = pd.DataFrame(user_similarity, 
                                        index=interaction_matrix.index, 
                                        columns=interaction_matrix.index)

        # Check if we can find similar users
        if self.id not in user_similarity_df.columns:
            print("No similar users found.")
            return []  # Return empty if no similarity could be computed

        # Get the similarity scores for the target blog (self.id)
        similar_users = user_similarity_df[self.id].sort_values(ascending=False)[1:top_n+1].index

        # Debugging: Check if similar users are found
        print(f"Similar Users: {similar_users}")

        # Get blog posts interacted with by similar users
        similar_users_interactions = interaction_matrix.loc[similar_users]

        # Sum the interactions for each blog post across these similar users
        post_scores = similar_users_interactions.sum(axis=0)

        # Sort blog posts by score in descending order
        recommended_posts = post_scores.sort_values(ascending=False)

        # Debugging: Check the recommended posts (before filtering)
        print(f"Recommended Posts (before filtering): {recommended_posts}")

        # Filter out posts the user has already interacted with
        user_interactions = interaction_matrix.loc[self.id]
        recommended_posts = recommended_posts[user_interactions == 0]

        # Debugging: Check the recommended posts (after filtering)
        print(f"Recommended Posts (after filtering): {recommended_posts}")

        # Get the top N recommended blog posts
        top_recommended_posts = recommended_posts.head(top_n)

        # Fetch the recommended blog details
        recommended_blogs = PublicLetter.objects.filter(id__in=top_recommended_posts.index)

        # Debugging: Check if recommended blogs are returned
        print(f"Recommended blogs: {[blog.title for blog in recommended_blogs]}")

        return recommended_blogs

# Signal to Sync PublicLetter with Letter
@receiver(post_save, sender=Letter)
def sync_to_public_letter(sender, instance, created, **kwargs):
    """
    Automatically create or update a PublicLetter when a Letter is saved with is_public=True.
    Deletes the PublicLetter if is_public=False.
    """
    if instance.is_public:
        public_letter, created = PublicLetter.objects.get_or_create(
            original_letter=instance,
            defaults={
                'shared_by': instance.user,
                'title': instance.title,
                'description': instance.content,
                'is_published': False,
            }
        )
        if not created:
            public_letter.title = instance.title or public_letter.title
            public_letter.description = instance.content or public_letter.description
            public_letter.shared_by = instance.user or public_letter.shared_by
            public_letter.is_published = False
            public_letter.save()
        
        if instance.user:
            public_letter.nickname = instance.user.username
        else:
            public_letter.nickname = "Anonymous"
        
        public_letter.save()
    else:
        PublicLetter.objects.filter(original_letter=instance).delete()




class BlogInteraction(models.Model):
    """
    Model to store the interaction data of a user with a blog post.
    """
    public_letter = models.ForeignKey(PublicLetter, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_interactions')  # Make this field nullable
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For anonymous users
    interaction_type = models.CharField(max_length=50, choices=[
        ('view', 'View'),
        ('click', 'Click'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        # Add any other interactions you want to track
    ])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interaction_type} by {'Anonymous' if not self.user else self.user} on {self.public_letter.title}"



class LetterReaction(models.Model):
    public_letter = models.ForeignKey(
        'PublicLetter',
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Allow NULL values in the database
        blank=True  # Allow empty values in forms
    )
    reacted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('public_letter', 'user')  # Ensures one like per user per letter

    def __str__(self):
        return f"Like by {self.user} on {self.public_letter}"
# letter comments

class Comment(models.Model):
    # Linking the comment to a public letter

    public_letter = models.ForeignKey(PublicLetter, on_delete=models.CASCADE, related_name='comments')
    # User who wrote the comment
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # The content of the comment
    content = models.TextField()
    # Timestamp when the comment was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional field for replying to another comment
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user or 'Anonymous'} on {self.public_letter}"
    
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete= models.CASCADE)
    body = models.TextField()
def __str__(self):
    return self.title + '|' + str(self.author)
