import random
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,JsonResponse
from .models import Tweet
# Create your views here.


def home_view(request):
    return render(request,'pages/home.html',{},status=200)

def tweet_list_view(request,*args,**kwargs):

    qs=Tweet.objects.all()
    tweets_list=[{'id':x.id,'content':x.content,"likes":random.randint(0,20000)} for x in qs]
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