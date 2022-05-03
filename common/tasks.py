from project.celery import app
from django.core.mail import send_mail
from django.conf import settings


@app.task
def sendMailTask(subject, message, recipient_list):
    ret = send_mail(subject=subject, message=message,
          from_email=settings.EMAIL_HOST_USER,
          recipient_list=recipient_list,
          fail_silently=False)
    print("ret=%s" %ret)   
       