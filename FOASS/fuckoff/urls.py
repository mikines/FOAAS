from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.login),
	url(r'^style.css',TemplateView.as_view(template_name="style.css")),
]
