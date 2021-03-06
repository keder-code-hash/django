from typing import Dict
import json
from django.contrib.auth.hashers import make_password
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView
from .serializers import userSerializer,RegisterSerializers,RegisterUpdateSerializer
from .models import Register
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from rest_framework.response import Response
from users.jwtAuth import JWTAuthentication
from users.token_generator import get_access_token,get_refresh_token
from django.shortcuts import render
from django.http import HttpResponseRedirect
#user view or delete.
from django.shortcuts import render, redirect
from .forms import RegisterForm,LogInForm,profileForm ,resetPassInit
from rest_framework import exceptions
from django.urls import reverse
import jwt
from rest_framework import exceptions
from django.conf import settings
from posts.models import PostRate, Posts,postTag,Comments 
import datetime
from django.http import Http404
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect, requires_csrf_token,ensure_csrf_cookie,csrf_exempt
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import get_template
from django.core.mail import EmailMessage
from posts.handle_upload import *
from django.template import Context, context
# from 

class Users(APIView):
    # authentication_classes =[JWTAuthentication]
    # permission_classes=[IsAdminUser]
    # @csrf_protect
    def get(self,request,format=None):
        queryset=Register.objects.all()
        serialized_data=userSerializer(queryset,many=True)
        return Response(serialized_data.data,status.HTTP_200_OK)
    def delete(self,request,format=None):
        if Register.objects.filter(email__iexact=request.data['email']).exists():
            Register.objects.filter(email__iexact=request.data['email']).delete()
            return Response("User deleted successfully.",status.HTTP_200_OK)



#register.
class UserRegister(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request):
        if Register.objects.filter(email__iexact=request.data['email']).exists():
            user_data=Register.objects.get(email__iexact=request.data['email'])
            serialized_data=userSerializer(user_data)
            return Response(serialized_data.data,status.HTTP_200_OK)
        else:
            return Response("User does not exist",status.HTTP_404_NOT_FOUND)
    def post(self,request,format=None):
        if Register.objects.filter(email__iexact=request.data['email']).exists()==False:
            serialized=RegisterSerializers(data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response("User successfully created",status.HTTP_200_OK)
            else:
                return Response(serialized.errors,status.HTTP_400_BAD_REQUEST)
        else:
            return Response("User already exist with same email.",status.HTTP_226_IM_USED)

    def put(self,request,format=None):
        if Register.objects.filter(email__iexact=request.data['email']).exists():
            reg_user=Register.objects.get(email=request.data['email'])
            serialized_data=RegisterSerializers(instance=reg_user,data=request.data)
            if serialized_data.is_valid():
                serialized_data.save()
                return Response("User successfully updated",status.HTTP_200_OK)
            else:
                return Response(serialized_data.errors,status.HTTP_200_OK)


class userLogin(APIView):
    permission_classes=[AllowAny]
    def post(self,request,*args,**kwargs):
        username=request.data['username']
        password=request.data['password']
        response=Response()
        if username and password is not None:
            if Register.objects.filter(email=username).exists():
                user_data=Register.objects.get(email=username)
                if user_data.check_password(password)==True:
                    access_token=get_access_token(user_data)
                    refresh_token=get_refresh_token(user_data)
                    response.set_cookie(key='refreshtoken',value=refresh_token,httponly=True)
                    response.data={
                        "token":access_token,
                        "username":user_data.user_name
                    }
                    return response
                else:
                    return Response("wrong credentialS.",status.HTTP_400_BAD_REQUEST)
            else:
                return Response("wrong credentialS.",status.HTTP_400_BAD_REQUEST)
        else:
            return Response("values can not be NULL.",status.HTTP_400_BAD_REQUEST)



############################################################

def register_view(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            data={
                'first_name':form.cleaned_data['first_name'],
                'last_name':form.cleaned_data['last_name'],
                'user_name':form.cleaned_data['user_name'],
                'email':form.cleaned_data['emailid'],
                'password':form.cleaned_data['user_password']
            }
            if Register.objects.filter(email__iexact=data['email']).exists() ==False:
                serialized=RegisterSerializers(data=data)
                if serialized.is_valid():
                    serialized.save()
                else:
                    raise exceptions.ValidationError(serialized.error_messages())
                return HttpResponseRedirect(reverse('homePage'))
            else:
                return HttpResponse("User already exist with same email.")
    else:
        form=RegisterForm()
    return render(request,'signup.html',{'form':form})    

def login_view(request):
    if request.method=='POST':
        form=LogInForm(request.POST)
        # print(form)
        if form.is_valid():
            data={
                'email':form.cleaned_data['emailid'],
                'password':form.cleaned_data['user_password']
            }
            user_data=Register.objects.get(email__exact=data.get('email'))
            if user_data.check_password(data.get('password'))==True:
                response=HttpResponseRedirect(reverse('homePage'))
                data={
                    'last_login':datetime.datetime.now(datetime.timezone.utc)
                }
                for key,val in data.items():
                        setattr(user_data,key,val)
                user_data.save()
                access_token = get_access_token(user_data)
                refresh_token = get_refresh_token(user_data)
                response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
                response.set_cookie(key='accesstoken',value=access_token,httponly=True)
                response.data = {
                    "token": access_token,
                    "username": user_data.user_name
                }
                return response
            else:
                pass
        else:
            pass
    else:
        form=LogInForm()
    return render(request,'login.html',{'form':form})

def custom_log_out(request):
    access_token=request.COOKIES.get('accesstoken')
    refresh_token=request.COOKIES.get('refreshtoken')
    response=HttpResponseRedirect(reverse('homePage'))
    if (access_token is not None) and (refresh_token is not None):
        response.delete_cookie('accesstoken')
        response.delete_cookie('refreshtoken')
        return response
    else:
        return response



def is_authenticated_user(request):
    access_token = request.COOKIES.get('accesstoken')
    if access_token is not None:
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms="HS256")
            email = payload['email']
            user = Register.objects.get(email=email)
            if user is not None:
                return True
            else:
                return False
        except jwt.ExpiredSignatureError as ex:
            custom_log_out(request)
        except jwt.DecodeError:
            return False
        except Register.DoesNotExist as ne:
            raise exceptions.AuthenticationFailed('invalid email id')
    else:
        return False

def userProfileView(request):
    # add image option in update profile
    # if request.method == "GET":
    #     try:
    #         access = request.COOKIES.get('accesstoken')
            try:
                payload_data=jwt.decode(request.COOKIES.get('accesstoken'),settings.SECRET_KEY,algorithms="HS256")
                email=payload_data.get('email')
                try:
                    user=Register.objects.get(email__iexact=email)
                    postNo=Posts.objects.filter(owner__email=user.email).count()
                    commentNo=Comments.objects.filter(owner__email=user.email).count()
                    current_year=datetime.datetime.now().year
                    user_db=str(user.date_of_birth)
                    age=user_db
                    context={
                        'is_authenticated': is_authenticated_user(request),
                        'postNo':postNo,
                        'commentNo':commentNo,
                        'user':user,
                        'age':age
                    }
                    return render(request,'userProfile.html',context)
                except Register.DoesNotExist as err:
                    raise exceptions.AuthenticationFailed('Invalid email id.')
            except jwt.ExpiredSignatureError or jwt.DecodeError:
                return custom_log_out(request)
        # except ValueError as err:
        #     print("hiii")
        #     return redirect('homePage')
    # return render(request,'userProfile.html')

def truncateP(string,maxLength):
    spceList=str(string).split(" ")
    currStr=str("") 
    currStr=spceList[0:maxLength]
    newStr=str("")
    for s in currStr:
        newStr+=s+" "
    return newStr

def homeView(request):
    if request.method=="GET":
        all_blogs=Posts.objects.filter(status='p').order_by('post_created').values()

        blogs=Posts.objects.filter(status='p').order_by('post_created').values('id','post_created','post_title')
        filtered_data=list(blogs)
        # print(filtered_data)

        for blg in all_blogs:
            p=postTag.objects.filter(posts__id=blg.get('id')).values('tag_name')
            blg['tags']=p

        dataDict=dict()
        postName=dict()
        for raw in filtered_data:
            if raw.get('post_created').year not in dataDict.keys():
                dataDict[raw.get('post_created').year]=[[] for i in range(12)]
            if raw.get('id')not in postName.keys():
                postName[raw.get('id')]=''
            postName[raw.get('id')]=raw.get('post_title')
            month_no=raw.get('post_created').month-1
            dataDict[raw.get('post_created').year][month_no].append(raw.get('id'))

        dataDictJson=json.dumps(dataDict, separators=(',', ':'))

        # print(Posts.objects.all()[0])
        # print(list(yearList))

        # print(json.loads(all_blogs[0].get('body_custom')))
        # add some data to eact post qs...
        for i in range(len(all_blogs)):
            jsonifyData=json.loads(all_blogs[i].get('body_custom'))
            for block in jsonifyData.get('blocks'):
                try:
                    if(block.get('type')=='paragraph'):
                        all_blogs[i]['paraData']=truncateP(block.get('data').get('text'),100)
                        break
                except ValueError:
                    pass
            noOfComments=Comments.objects.filter(post__id=all_blogs[i].get('id')).count()
            Ratings=PostRate.objects.filter(post_id__id=all_blogs[i].get('id')).count()
            all_blogs[i]['comment_no']=noOfComments
            all_blogs[i]['rated_no']=Ratings
            all_blogs[i]['user_info']=Register.objects.filter(email=all_blogs[i].get('owner_id')).values('user_name','profile_pic_url')[0]
            currentTime=datetime.datetime.now(datetime.timezone.utc)
            daysDiff=currentTime-all_blogs[i].get('post_created')
            all_blogs[i]['days_diff']=daysDiff.days
            # print()
        # print(all_blogs[0]['user_info'].get('profile_pic'))
        # print(all_blogs[0])

        # page=request.GET.get('page',1)
        # paginator=Paginator(all_blogs,3)

        allTags=postTag.objects.all().values()
        # try:
        #     posts=paginator.page(page)
        # except PageNotAnInteger:
        #     posts=paginator.page(1)
        # except:
        #     posts=paginator.page(paginator.num_pages)

        context={
            'is_authenticated':is_authenticated_user(request),
            'posts':all_blogs,
            'postTreeData':dataDictJson,
            'postDet':json.dumps(postName),
            'allTags':allTags
        }
        # print(request.GET)
        return render(request,'Home.html',context)

def postViewByTag(request,tag_name):
    if request.method=="GET":
        # print(tag_name)
        all_blogs=Posts.objects.filter(status='p').filter(tag__tag_name=tag_name).order_by('post_created').values()

        blogs=Posts.objects.filter(status='p').order_by('post_created').values('id','post_created','post_title')
        filtered_data=list(blogs)
        for blg in all_blogs:
            p=postTag.objects.filter(posts__id=blg.get('id')).values('tag_name')
            blg['tags']=p

        # print(all_blogs[0].get('tags'))
        
        
        dataDict=dict()
        postName=dict()
        for raw in filtered_data:
            if raw.get('post_created').year not in dataDict.keys():
                dataDict[raw.get('post_created').year]=[[] for i in range(12)]
            if raw.get('id')not in postName.keys():
                postName[raw.get('id')]=''
            postName[raw.get('id')]=raw.get('post_title')
            month_no=raw.get('post_created').month-1
            dataDict[raw.get('post_created').year][month_no].append(raw.get('id'))

        dataDictJson=json.dumps(dataDict, separators=(',', ':'))

        for i in range(len(all_blogs)):
            jsonifyData=json.loads(all_blogs[i].get('body_custom'))
            for block in jsonifyData.get('blocks'):
                try:
                    if(block.get('type')=='paragraph'):
                        all_blogs[i]['paraData']=truncateP(block.get('data').get('text'),100)
                        break
                except ValueError:
                    pass
            noOfComments=Comments.objects.filter(post__id=all_blogs[i].get('id')).count()
            Ratings=PostRate.objects.filter(post_id__id=all_blogs[i].get('id')).count()
            all_blogs[i]['comment_no']=noOfComments
            all_blogs[i]['rated_no']=Ratings
            all_blogs[i]['user_info']=Register.objects.filter(email=all_blogs[i].get('owner_id')).values('user_name','profile_pic_url')[0]
            currentTime=datetime.datetime.now(datetime.timezone.utc)
            daysDiff=currentTime-all_blogs[i].get('post_created')
            all_blogs[i]['days_diff']=daysDiff.days

        page=request.GET.get('page',1)
        paginator=Paginator(all_blogs,3)
        
        allTags=postTag.objects.all().values()
        try:
            posts=paginator.page(page)
        except PageNotAnInteger:
            posts=paginator.page(1)
        except:
            posts=paginator.page(paginator.num_pages)

        context={
            'is_authenticated':is_authenticated_user(request),
            'posts':posts,
            'postTreeData':dataDictJson,
            'postDet':json.dumps(postName),
            'allTags':allTags
        }
        # print(request.GET)
        return render(request,'Home.html',context)



def upDateProfile(request):
    access = request.COOKIES.get('accesstoken')
    decoded_data = jwt.decode(access, settings.SECRET_KEY, algorithms="HS256")
    email_id = decoded_data.get('email')
    user = Register.objects.get(email__iexact=email_id)
    if request.method == 'POST':
        form=profileForm(request.POST,request.FILES)
        if form.is_valid():
            data={
                'user_name':form.cleaned_data.get('user_name'),
                'first_name':form.cleaned_data.get('first_name'),
                'last_name':form.cleaned_data.get('last_name'),
                'interests':form.cleaned_data.get('interests'),
                'bio':form.cleaned_data.get('bio'),
                'date_of_birth':form.cleaned_data.get('date_of_birth'),
                'ph_no': form.cleaned_data.get('ph_no'),
            }
            # print(data)
            try:
                user_data=Register.objects.get(email=email_id)
                for key,val in data.items():
                    setattr(user_data,key,val)
                user_data.save()
            except Register.DoesNotExist:
                user_data=Register(**data)
                user_data.save()
           
            if request.FILES:
                # default_storage.save(request.FILES['profile_pic'].name, request.FILES['profile_pic'])
                # fs=FileSystemStorage(location=settings.MEDIA_ROOT+'/uploads/profile/')
                # fs.save(request.FILES['profile_pic'].name, request.FILES['profile_pic'])
                profile_pic=request.FILES['profile_pic']
                profile_pic_name=request.FILES['profile_pic'].name
                profile_pic_url=upload_image(profile_pic,profile_pic_name,"Blog/Profile/").get("secure_url")
                Register.objects.filter(email__iexact=user.email).update(profile_pic_url=profile_pic_url)
            return redirect('profile')
            
    form=profileForm()
    context={
        'is_authenticated':is_authenticated_user(request),
        'user':user,
        'form':form,
        'user_name': user.user_name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'interests': user.interests,
        'bio': user.bio,
        'date_of_birth': user.date_of_birth,
        'ph_no': user.ph_no, 
        'profile_pic_url':user.profile_pic_url
    }
    # print(context)
    return render(request, 'updateprofile.html',context)

@csrf_exempt
def contactForm(request):
    if request.method=='POST':
        name=request.POST.get('firstName')+request.POST.get('lastName')
        email=request.POST.get('email')
        message=request.POST.get('message')

        subject,from_email,to='contact',"kedernath.mallick.tint022@gmail.com","kedernath.mallick.tint022@gmail.com"
        text_context=f'{name}wants to contact with you'
        html_content='<p><strong>EMAIL:</strong>'+email+'</p><br><h4>MESSAGE:</h4>'+message
        msg=EmailMultiAlternatives(subject,text_context,from_email,[to])
        msg.attach_alternative(html_content,'text/html')
        msg.send()
        
    return HttpResponse({"msg":"success"})

# @csrf_exempt
def resetPassword(request,token):
    if request.method=='POST': 
        access_tok=token
        password=request.POST.get('password')
        conf_password=request.POST.get('conf_password') 
        if password!=conf_password: 
            msg={
                'st':'nm'
            }
            return JsonResponse(msg)
        else:
            try:
                payload = jwt.decode(access_tok, settings.SECRET_KEY, algorithms="HS256")
                email = payload['email']
                try:
                    new_pass=make_password(password)
                    data={
                        'password':new_pass
                    }
                    user = Register.objects.get(email=email)
                    for key,val in data.items():
                        setattr(user,key,val)
                    user.save()
                    msg={
                        "st":"su"
                    }
                    return JsonResponse(msg)
                except Register.DoesNotExist:
                    print("user does not exist")
            except jwt.ExpiredSignatureError as ex:
                msg={
                        "st":"le"
                    }
                return JsonResponse(msg)
            except jwt.DecodeError:
                print("ERROR")
            except Register.DoesNotExist as ne:
                raise exceptions.AuthenticationFailed('invalid email id') 
    # print(make_password("token")) 
    context={
        'token':token,
        'is_authenticated':is_authenticated_user(request)
    }
    return render(request,'resetPassword.html',context)


@csrf_exempt
def resetPasswordInit(request):
    if request.method=='POST':
        email=request.POST.get('email')
        user=Register.objects.filter(email=email)
        print(email)
        if user.exists() is False:
            msg={
                "st":"er",
                "ms":"please give the verified email with your account"
            }
            return JsonResponse(msg)
        else:
            msg={
                "st":"su",
                "ms":"We have e-mailed your password reset link!"
            }
            access_token=get_access_token(Register.objects.get(email=email)) 
            ctx={
                'resetPass_url':'http://127.0.0.1:8000/'+'reset_password/'+access_token
            }
            message = get_template("emails/reset_pass.html").render(ctx)
            mail = EmailMessage(
                subject="Reset Password",
                body=message,
                from_email="kedernath.mallick.tint022@gmail.com",
                to=["kedernath.mallick.tint022@gmail.com"],
                reply_to=["kedernath.mallick.tint022@gmail.com"],
            )
            mail.content_subtype = "html"
            mail.send() 
            
            return JsonResponse(msg)
    context={
        'is_authenticated':is_authenticated_user(request),
    }
    return render(request,'resetPasswordInit.html',context)