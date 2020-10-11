from django.shortcuts import render, redirect
from django.urls import reverse
from user.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login as login_admin
import os
from announcement.models import Announcement, AnnouncementRecord, Feedback
from django.http import HttpResponse
from PIL import Image
from announcement.models import image_path
from teamwork import settings
from teamwork.settings import MEDIA_URL
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import uuid
import re
from django.utils.datastructures import MultiValueDictKeyError


def check_authority(func):
    def wrapper(*args, **kwargs):
        username = args[0].session.get("login_user", "")
        if username == "":
            args[0].session["path"] = args[0].path
            return redirect(reverse("login"))
        return func(*args, **kwargs)
    return wrapper


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        if not check_register_valudate(request, check_username_validate, check_password_validate, check_lastname_validate,
                                       check_firstname_validate, check_teamname_validate):
            return HttpResponse("注册失败!")
        username = request.POST.get("username")
        password = request.POST.get("password")
        lastname = request.POST.get("lastname")
        firstname = request.POST.get("firstname")
        teamname = request.POST.get("teamname")
        try:
            teamid = uuid.uuid4().hex
            User.objects.create(username=username, password=make_password(password), last_name=lastname,
                                first_name=firstname, team_name=teamname, team_id=teamid, is_active=True, is_staff=True,
                                is_superuser=True)
            user = User.objects.get(username=username)
            login_admin(request, user)
            return redirect('../admin/')
        except:
            return HttpResponse("注册失败!")
    else:
        return render(request, "register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            is_valid = check_password(password, user.password)
        except:
            is_valid = False
        if is_valid:
            request.session["login_user"] = username
            request.session.set_expiry(1209600)
            login_admin(request, user)
            path = request.session.get("path", "")
            if path != "":
                return redirect(request.session["path"])
            else:
                return redirect('../admin/')
        else:
            return HttpResponse("登录失败，请确认用户名和密码是否正确!")
    else:
        username = request.session.get("login_user", "")
        if username == "":
            return render(request, "login.html")
        else:
            return redirect('../admin/')


@check_authority
def make_announcement(request, id):
    try:
        current_username = request.user.full_name
    except:
        current_username = User.objects.get(username=request.session["login_user"]).full_name
    announcement = Announcement.objects.get(id=id)
    feedback = Feedback.objects.filter(aid=id)
    to_group_obj = announcement.to_group.all()
    to_people_obj = announcement.to_people.all()
    to_people = [i.full_name for i in to_people_obj] if len(to_people_obj) != 0 else []
    to_people_extend = to_people.copy()
    group_dict = {}
    if len(to_group_obj) != 0:
        for group_obj in to_group_obj:
            group_mamber = [i.full_name for i in group_obj.member.all()]
            group_dict[group_obj.name] = [group_mamber]
            to_people_extend += group_mamber
    if len(to_people_extend) != 0:
        to_people_extend = list(set(to_people_extend))
    read_names_extend = AnnouncementRecord.objects.filter(aid=id)
    read_names_extend = list(read_names_extend.values_list("reader", flat=True))
    if current_username not in to_people_extend:
        is_read = True
    else:
        is_read = True if current_username in read_names_extend else False
    if len(read_names_extend) != 0:
        if len(group_dict) != 0:
            for name, member in group_dict.items():
                group_dict[name].append([i for i in read_names_extend if i in member[0]])
                group_dict[name].append([i for i in member[0] if i not in member[1]])
        read_names = [name for name in to_people if name in read_names_extend]
        unread_names = [name for name in to_people if name not in read_names_extend]
    else:
        if len(group_dict) != 0:
            for name, member in group_dict.items():
                group_dict[name].append([])
                group_dict[name].append(member[0])
        read_names = []
        unread_names = to_people
    to_people_length = (len(to_people))
    values = {'id': id, 'announcement': announcement, 'group_dict': group_dict, 'read_names': read_names,
              'unread_names': unread_names, 'is_read': is_read, 'to_people_length': to_people_length,
              'feedback': feedback}
    return render(request, 'announcement.html', values)


@check_authority
def read_confirm(request, id, require_upload):
    # 对应action中 <form action = "{% url 'confirm' id %}" method = "post"> 的 {% url 'confirm' id %} 方法，
    # confirm指向urls.py中name=confirm的url
    user = request.session.get("login_user", "")
    user = User.objects.get(username=user).full_name
    if len(AnnouncementRecord.objects.filter(aid=id, reader=user)) > 0:
        return HttpResponse("您已经提交确认，请勿重复提交！")
    else:
        if require_upload == "True":
            try:
                img = request.FILES["img"]
            except:
                img = None
            if img is not None:
                img_name = img.name.lower()
                if img_name.endswith("jpg") or img_name.endswith("jpeg") or img_name.endswith("png"):
                    try:
                        img_type = img_name.split(".")[-1]
                        img = Image.open(img)
                        x, y = img.size
                        if x > y:
                            img = img.rotate(90, expand=True)
                        img = img.resize((392, 700))
                        img.save(os.path.join(settings.MEDIA_ROOT, image_path, (id + '_' + user + '.' + img_type)))
                    except:
                        return HttpResponse("图片格式错误，请尝试重新上传或更换图片！")
                    AnnouncementRecord.objects.create(aid=id, reader=user, image=os.path.join(image_path, (
                                id + '_' + user + '.' + img_type)))
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    return HttpResponse("图片格式错误，，请尝试重新上传或更换图片！")
            else:
                return HttpResponse("图片未上传！")
        else:
            AnnouncementRecord.objects.create(aid=id, reader=user)
            return redirect(request.META['HTTP_REFERER'])


@check_authority
def feedback_confirm(request, id):
    # 对应action中 <form action = "{% url 'feedback_confirm' id %}" method = "post"> 的 {% url 'feedback_confirm' id %} 方法，
    # confirm指向urls.py中name=confirm的url
    user = request.session.get("login_user", "")
    user = User.objects.get(username=user).full_name
    comment = request.POST.get("feedback")
    if len(Feedback.objects.filter(aid=id, sender=user)) > 3:
        return HttpResponse("您的评论次数过多，已经限制评论，请勿刷屏！")
    else:
        Feedback.objects.create(aid=id, sender=user, comment=comment)
        return redirect(request.META['HTTP_REFERER'])


@csrf_exempt
def show_upload(request, id, names=None):
    if request.method == "POST":
        if names is not None:
            values = AnnouncementRecord.objects.filter(aid=id)
            if len(values) != 0:
                try:
                    values = {"reader_upload": {values.get(reader=name).reader: values.get(reader=name).image
                                                for name in values.values_list("reader", flat=True) if name in names},
                              "media_url": MEDIA_URL}
                    return render(request, "show-upload.html", values)
                except:
                    return HttpResponse("请求错误！请从公告阅读界面访问该页。")
            else:
                return HttpResponse("没有公告确认记录！")
        else:
            return HttpResponse("请求错误！请从公告阅读界面访问该页。")
    else:
        return HttpResponse("请求错误！请从公告阅读界面访问该页。")


def check_username_validate(request):
    try:
        username = request.GET["username"]
    except MultiValueDictKeyError:
        username = request.POST.get("username")
    if username == "":
        return HttpResponse('用户名不能为空')
    if len(username) < 4 or len(username) > 16:
        return HttpResponse('用户名不能少于4个字符或超过16个字符')
    if not re.search(r'^[_a-zA-Z0-9]+$', username):
        return HttpResponse("用户名包含非法字符(!,@,#,$,%...)")
    if User.objects.filter(username=username).count() != 0:
        return HttpResponse('用户名已存在')
    return HttpResponse('')


def check_password_validate(request):
    try:
        password = request.GET["password"]
    except MultiValueDictKeyError:
        password = request.POST.get("password")
    if password == "":
        return HttpResponse('密码不能为空')
    if len(password) < 6 or len(password) > 16:
        return HttpResponse('密码不能少于6个字符或超过16个字符')
    if not re.search(r'^\S+$', password):
        return HttpResponse("密码包含非法字符(‘ ’)")
    return HttpResponse('')


def check_lastname_validate(request):
    try:
        lastname = request.GET["lastname"]
    except MultiValueDictKeyError:
        lastname = request.POST.get("lastname")
    if lastname == "":
        return HttpResponse('姓氏不能为空')
    if len(lastname) > 50:
        return HttpResponse('姓氏不能超过50个字符')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', lastname):
        return HttpResponse("姓氏包含非法字符(!,@,#,$,%...)")
    return HttpResponse('')


def check_firstname_validate(request):
    try:
        firstname = request.GET["firstname"]
    except MultiValueDictKeyError:
        firstname = request.POST.get("firstname")
    if firstname == "":
        return HttpResponse('名字不能为空')
    if len(firstname) > 50:
        return HttpResponse('名字不能超过50个字符')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', firstname):
        return HttpResponse("名字包含非法字符(!,@,#,$,%...)")
    return HttpResponse('')


def check_teamname_validate(request):
    try:
        teamname = request.GET["teamname"]
    except MultiValueDictKeyError:
        teamname = request.POST.get("teamname")
    if teamname == "":
        return HttpResponse('团队名称不能为空')
    if len(teamname) > 16:
        return HttpResponse('团队名称不能超过16个字符')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', teamname):
        return HttpResponse("输入包含非法字符(!,@,#,$,%...)")
    return HttpResponse('')


def check_register_valudate(request, *args):
    check_method = args
    for method in check_method:
        if method(request).content != b'':
            return False
    return True


# scheduler = BackgroundScheduler()
# scheduler.add_jobstore(DjangoJobStore(), "default")
#
#
# @register_job(scheduler, "interval", hours=1, id="clean_expired_data")
# def clean_expired_data():
#     data = Announcement.objects.filter(deadline__lte=timezone.now(), active=True)
#     if len(data) > 0:
#         data_id = list(set(data.values_list("id", flat=True)))
#         data.update(content="已过期", active=False)
#         data_id = [str(i) for i in data_id]
#         dir = os.path.join(settings.MEDIA_ROOT, image_path)
#         for file in os.listdir(dir):
#             if file.startswith(tuple(data_id)):
#                 os.remove(os.path.join(dir, file))
#
#
# register_events(scheduler)
# scheduler.start()
