import graphene
import graphql_jwt
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from .models import User, Post
from django.contrib.auth import get_user_model

class UserType(DjangoObjectType):
    class Meta:
        model = User

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class PostType(DjangoObjectType):
    class Meta:
        model = Post

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    posts = graphene.List(PostType)

    @login_required
    def resolve_users(self, info):
        return User.objects.all()

    @login_required
    def resolve_posts(self, info):
        return Post.objects.all()


class CreatePostMutation(graphene.Mutation):
    post = graphene.Field(PostType)
    
    class Arguments:

        title = graphene.String(required=True)
        content = graphene.String(required=True)
    
    @login_required
    def mutate(self, info, title, content):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('You must be logged in to create a post')
        post = Post.objects.create(title=title, content=content, user=user)
        return CreatePostMutation(post=post)

class UpdatePostMutation(graphene.Mutation):
    post = graphene.Field(PostType)
    
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        content = graphene.String()
    
    @login_required
    def mutate(self, info, id, title=None, content=None):
        user = info.context.user

        post = Post.objects.get(id=id)
        if post.user != user:
            raise Exception('You can only update your own posts')
        if title:
            post.title = title
        if content:
            post.content = content
        post.save()
        return UpdatePostMutation(post=post)

class DeletePostMutation(graphene.Mutation):
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, id):
        user = info.context.user

        post = Post.objects.get(id=id)
        if post.user != user:
            raise Exception('You can only delete your own posts')
        post.delete()
        return DeletePostMutation(success=True)

class LikePostMutation(graphene.Mutation):
    post = graphene.Field(PostType)
    
    class Arguments:
        id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, id):
        user = info.context.user
        
        post = Post.objects.get(id=id)
        if user in post.likes.all():
            raise Exception('You have already liked this post')
        post.likes.add(user)
        return LikePostMutation(post)

class UnlikePostMutation(graphene.Mutation):
    post = graphene.Field(PostType)
    
    class Arguments:
        id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, id):
        user = info.context.user
        post = Post.objects.get(id=id)
        if user not in post.likes.all():
            raise Exception('You have not liked this post')
        post.likes.remove(user)
        return UnlikePostMutation(post)

        
class CreateUserMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(lambda: UserType)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return CreateUserMutation(user=user)


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.Int(required=True)
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()

    def mutate(self, info, id, username=None, password=None, email=None):
        user = get_user_model().objects.get(pk=id)
        if username:
            user.username = username
        if password:
            user.set_password(password)
        if email:
            user.email = email
        user.save()

        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        user = get_user_model().objects.get(pk=id)
        if not user:
            raise Exception('User does not exist')
        user.delete()

        return DeleteUser(success=True)


class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
    like_post = LikePostMutation.Field()
    unlike_post = UnlikePostMutation.Field()
    create_user = CreateUserMutation.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)