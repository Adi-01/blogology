from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from django.utils import timezone


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list(request):
    """
    List all posts.
    """
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail(request, pk):
    """
    Retrieve a specific post.
    """
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PostSerializer(post)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    #Adding the current date:
    data = request.data.copy()
    data['date_posted'] = timezone.now().date()

    # Serialize the data and create the post
    serializer = PostSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the post data with the author info
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    serializer = PostSerializer(posts, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def edit_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the logged-in user is the author of the post
    if post.author != request.user:
        return Response({"detail": "You can only edit your own posts."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # Return the post data for editing if it's a GET request
        serializer = PostSerializer(post)
        return Response(serializer.data)

    if request.method == 'PUT':
        # Handle the PUT request to update the post
        serializer = PostSerializer(post, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the logged-in user is the author of the post
    if post.author != request.user:
        return Response({"detail": "You can only delete your own posts."}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments(request, pk):
    comments = Comment.objects.filter(post_id=pk)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

# View to add a comment to a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, pk):
    data = request.data
    data['post'] = pk
    data['author'] = request.user.id
    

    print("Logged-in user: ", request.user)  # Debug print
    print("Data being passed to serializer:", data)  # Debug print

    serializer = CommentSerializer(data=data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to delete a comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user != comment.author:  # Ensure the user is the author of the comment
        return Response({"detail": "You don't have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)