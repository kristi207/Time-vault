from django.db import models
from django.contrib.auth.models import User
import numpy as np
from collections import Counter
import pandas as pd
from django.utils.timezone import now


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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

    def __str__(self):
        return f"Public Letter: {self.title or self.original_letter.title or 'The Letter From {self.shared_date}'}"

    @staticmethod
    def recommend_blogs():
        """
        Generate blog recommendations based on the description field using TF-IDF and cosine similarity.
        """

        # Fetch descriptions of published blogs
        public_letters = PublicLetter.objects.filter(is_published=False).values('id', 'description', 'title')
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
            recommended_blogs = df.iloc[similar_indices][['id','title', 'description']]
            return recommended_blogs

        # Add Recommendations to DataFrame
        df['recommended_blogs'] = [
            recommend_blogs(idx, similarity_matrix, df).to_dict(orient='records')
            for idx in range(len(df))
        ]

        # Return the dataframe for use in views or APIs
        return df[['id', 'title', 'recommended_blogs']].to_dict(orient='records')

# rection of letter

class LetterReaction(models.Model):
    # Linking the reaction to a public letter
    public_letter = models.ForeignKey(PublicLetter, on_delete=models.CASCADE, related_name='reactions')
    # Type of reaction (e.g., like, love, etc.)
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('inspired', 'Inspired'),
        ('wow', 'Wow'),
    ]
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    # User who reacted (optional for anonymous reactions)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Date of the reaction
    reacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reaction_type} by {self.user or 'Anonymous'} on {self.public_letter}"

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
    
