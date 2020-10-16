from django.db import models
from team.models import Team
from user.models import User


image_path = "image"


class Announcement(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=16, verbose_name="发布人")
    title = models.TextField(max_length=100, verbose_name="标题")
    content = models.TextField(max_length=800, verbose_name="内容")
    to_group = models.ManyToManyField(Team, related_name="to_group", blank=True, verbose_name="接收组")
    to_people = models.ManyToManyField(User, related_name="to_people", blank=True, verbose_name="接收人")
    require_upload = models.BooleanField(default=False, verbose_name="需要上传")
    issue_datetime = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    edit_datetime = models.DateTimeField(auto_now=True, verbose_name="最新修改时间")
    deadline = models.DateTimeField(blank=True, verbose_name="截止时间")
    url_address = models.TextField(max_length=200, blank=True, verbose_name="转发路径")
    active = models.BooleanField(default=True, verbose_name="启用")
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"

    def __str__(self):
        return self.title


class AnnouncementRecord(models.Model):
    id = models.AutoField(primary_key=True)
    aid = models.IntegerField(verbose_name="通知id")
    reader = models.CharField(max_length=16, verbose_name="阅读人")
    image = models.ImageField(upload_to=image_path, blank=True, verbose_name="图片")
    read_datetime = models.DateTimeField(auto_now=True, verbose_name="确认时间")
    read_status = models.CharField(max_length=10, verbose_name="阅读状态")
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    class Meta:
        verbose_name = "公告确认明细"
        verbose_name_plural = "公告确认明细"

    def __str__(self):
        return self.reader


class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    aid = models.IntegerField(verbose_name="通知id")
    sender = models.CharField(max_length=16, verbose_name="发送人")
    sent_datetime = models.DateTimeField(auto_now=True, verbose_name="发送时间")
    comment = models.TextField(max_length=100, verbose_name="内容")
    reply_to = models.IntegerField(null=True, verbose_name="回复id")
    team_id = models.CharField(max_length=32, null=True, verbose_name="团队id")

    class Meta:
        verbose_name = "留言"
        verbose_name_plural = "留言"

    def __str__(self):
        return self.sender
