from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    profile_picture = models.URLField(
        max_length=500,
        default='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png',
    )
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def to_public_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profile_picture,
            'isAdmin': self.is_admin,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
        }


class Post(models.Model):
    user_id = models.CharField(max_length=64)
    content = models.TextField()
    title = models.CharField(max_length=255, unique=True)
    image = models.URLField(
        max_length=500,
        default='https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png',
    )
    category = models.CharField(max_length=100, default='uncategorized')
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'content': self.content,
            'title': self.title,
            'image': self.image,
            'category': self.category,
            'slug': self.slug,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
        }


class Comment(models.Model):
    content = models.TextField()
    post_id = models.CharField(max_length=64)
    user_id = models.CharField(max_length=64)
    likes = models.JSONField(default=list)
    number_of_likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'postId': self.post_id,
            'userId': self.user_id,
            'likes': self.likes,
            'numberOfLikes': self.number_of_likes,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
        }
