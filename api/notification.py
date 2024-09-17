import os
import smtplib, jwt, datetime
import requests, uuid, secrets
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from rest_framework import viewsets, status, generics, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import UserSerializer, CustomUserSerializer, MessageSerializer, RoleSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from api.models import UserData, NotifyMessage
from api.pagination import CustomResponsePagination
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from .permission import CheckAuth



secret = os.environ.get('secret')
AUTHORIZATION = 'Authorization'
FRONTEND_URL = ""
admin = ''
domain = ''
pwd = ''
port = 465

def generate_code():
    code = secrets.token_urlsafe(12)
    return str(code)

def send_email_verification(url, to):
    try:
        response = Response()
        message = MIMEMultipart('alternative')

        message["Subject"] = "Verify Your emai"
        message["From"] = admin
        message['To'] = to

        plain_text = f"""\
        From: {admin}
        To: {to}
        Subject: Verify your email
        
        Please verify your email to gain full access to your account. Follow this link {url}
        """
        
        html_text = f"""\
        <html>
            <body>
                <h1>Verify Your email </h1>
                <p>Please verify your to gain full access to your account. 
                <a href="{url}">Click here</a> to verify.</p>
            </body>
        </html>
        """
        
        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(html_text, "html")

        message.attach(part1)
        message.attach(part2)

        smtp_server = smtplib.SMTP_SSL(domain, port)
        smtp_server.ehlo()
        smtp_server.login(admin, pwd)
        smtp_server.sendmail(admin, to, message.as_string())
        smtp_server.close()

        new_log = NotifyLog(time=timezone.now(), email_type="Email Verification", destination=to, status="delivered")
        new_log.save()

        response.data = {
            "ok": True,
            "details": "Email sent successfully!"
        }
        response.status_code = 200
    except KeyError:
        response.data = {
            "ok": False,
            "details": "Invalid request"
        }
        response.status_code = 400

    return response
