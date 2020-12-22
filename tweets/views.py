import random
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from django.utils.http import is_safe_url
from django.conf import settings
from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer,TweetActionSerializer,TweetCreateSerializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
# Create your views here.

ALLOWED_HOSTS=settings.ALLOWED_HOSTS

def home_view(request):    
    return render(request,'pages/home.html',{},status=200)

@api_view(['POST'])
# @authentication_classes([SessionAuthentication,])
@permission_classes([IsAuthenticated,])
def tweet_create_view(request,*args,**kwargs):

    serializer=TweetCreateSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data,status=201)
    return Response({},status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def tweet_action_view(request):
    """
    id is required.
    Action options are like,unlike,retweet
    
    """
    # print(request.POST)
    serializer=TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data=serializer.validated_data
        tweet_id=data.get('id')
        action=data.get('action')
        content=data.get('content')

        qs=Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({},status=404)
        obj=qs.first()

        if action=='unlike':
            obj.likes.remove(request.user)
            serializer=TweetSerializer(obj)
            return Response(serializer.data,status=200)

        elif action=='like':
            obj.likes.add(request.user)
            serializer=TweetSerializer(obj)
            return Response(serializer.data,status=200)
        elif action=='retweet':
            
            new_tweet=Tweet.objects.create(user=request.user,parent=obj,content=content)
            serializer=TweetSerializer(new_tweet)
            return Response(serializer.data,status=201)
    
   
    


@api_view(['GET'])
def tweet_list_view(request,*args,**kwargs):

    qs=Tweet.objects.all()
    serializer=TweetSerializer(qs,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tweet_detail_view(request,tweet_id):

    qs=Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({},status=404)
    serializer=TweetSerializer(qs.first())
    return Response(serializer.data,status=200)

@api_view(['DELETE','POST'])
@permission_classes([IsAuthenticated,])
def tweet_delete_view(request,tweet_id):
    
    qs=Tweet.objects.filter(id=tweet_id)
    # print(request.user,'--------',qs[0].pk,qs[0].user)
    if not qs.exists():        
        return Response({},status=404)
    qs=qs.filter(user=request.user)
    if not qs.exists():
        return Response({"message":"You cannot delete this tweet"},status=401)
    obj=qs.first()
    
    obj.delete()
    return Response({'message':"Tweet removed"},status=200)

def tweet_create_view_pure_django(request):
    user=request.user
    if not request.user.is_authenticated:
        user=None
        if request.is_ajax():
            return JsonResponse({},status=401)
        return redirect(settings.LOGIN_URL)
    
    print("ajax request",request.is_ajax())
    form=TweetForm(request.POST or None)
    next_url=request.POST.get("next") or None
    

    if form.is_valid():
        obj=form.save(commit=False)
        #can do something here
        obj.user=user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(),status=201)

        if next_url!=None and is_safe_url(next_url,ALLOWED_HOSTS):
            return redirect(next_url)
        form=TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors,status=400)

    return render(request,'components/form.html',context={"form":form})

def tweet_list_view_pure_django(request,*args,**kwargs):

    qs=Tweet.objects.all()
    tweets_list=[x.serialize() for x in qs]
    data={"response":tweets_list}
    return JsonResponse(data,status=200)

def tweet_detail_view_pure_django(request,tweet_id):
    data={
        'id':tweet_id,
      
        # 'image_path':obj.image.url,
    }
    try:
        obj=Tweet.objects.get(id=tweet_id)
        data['content']=obj.content
        status=200
    except:
        data['message']="Not found"
        status=404
    
    return JsonResponse(data,status=status)