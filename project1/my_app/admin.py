from django.contrib import admin

from .models import Post

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "content")

    # def like_count(self, obj):
    #     obj2 = Post.objects.get(user=obj.user)
    #     return obj2.likes.count()


admin.site.register(Post, PostAdmin)