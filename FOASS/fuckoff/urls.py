from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^/?$', views.login),
	url(r'^authenticated/?$',views.twit_auth),
	url(r'^profile',views.show_profile),
	url(r'^style.css',TemplateView.as_view(template_name="style.css")),
	url(r'^test',TemplateView.as_view(template_name="foaas3.html")),
	url(r'^add_target',views.addtarget),
	url(r'^add_mess',views.addmessage,name='addmess'),
	url(r'^logout',views.twit_logout),
	url(r'^allfucks',views.get_all_fucks),
	url(r'^validate',views.validate),
]
