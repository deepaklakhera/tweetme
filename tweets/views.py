import random
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from django.utils.http import is_safe_url
from django.conf import settings
from .models import Tweet
from .forms import TweetForm
# Create your views here.

ALLOWED_HOSTS=settings.ALLOWED_HOSTS

def home_view(request):
    return render(request,'pages/home.html',{},status=200)

def tweet_create_view(request):
    
    print("ajax request",request.is_ajax())
    form=TweetForm(request.POST or None)
    next_url=request.POST.get("next") or None
    

    if form.is_valid():
        obj=form.save(commit=False)
        #can do something here
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

def tweet_list_view(request,*args,**kwargs):

    qs=Tweet.objects.all()
    tweets_list=[x.serialize() for x in qs]
    data={"response":tweets_list}
    return JsonResponse(data,status=200)

def tweet_detail_view(request,tweet_id):
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