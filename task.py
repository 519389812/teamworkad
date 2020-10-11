import django
import os
import sys
path = '/home/teamwork/teamwork'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'teamwork.settings'
django.setup()
from django.utils import timezone
from announcement.models import Announcement, image_path
from teamwork import settings


def clean_expired_data():
    data = Announcement.objects.filter(deadline__lte=timezone.now(), active=True)
    if len(data) > 0:
        data_id = list(set(data.values_list("id", flat=True)))
        data.update(content="已过期", active=False)
        data_id = [str(i) for i in data_id]
        dir = os.path.join(settings.MEDIA_ROOT, image_path)
        for file in os.listdir(dir):
            if file.startswith(tuple(data_id)):
                os.remove(os.path.join(dir, file))


if __name__ == "__main__":
    clean_expired_data()
