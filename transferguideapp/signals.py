from allauth.socialaccount.models import providers
from allauth.socialaccount.providers.google.provider import GoogleProvider


def populate_models(sender, **kwargs):
    from django.contrib.auth.models import User
    from django.contrib.auth.models import Group
    from django.contrib.sites.models import Site 
    from allauth.socialaccount.models import SocialApp

    if(not Group.objects.filter(name='admins').exists()):
        Group.objects.create(name='admins')
    if(not Group.objects.filter(name='users').exists()):
        Group.objects.create(name='users')
    if(not Site.objects.filter(name='localhost:8000').exists()):
        Site.objects.create(domain='localhost:8000', name='localhost:8000')
    if(not Site.objects.filter(name='transfer-guide.herokuapp.com').exists()):
        Site.objects.create(domain='transfer-guide.herokuapp.com', name='transfer-guide.herokuapp.com')
    if(not SocialApp.objects.filter(name='OAuth').exists()):
        sa = SocialApp(name="OAuth",client_id="23331016848-jkbo4pm74cepie6e2nn4sujq6nu4a90n.apps.googleusercontent.com", secret="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")
        sa.save()
        sa.provider = 'google'#GoogleProvider.name 
        sa.sites.add(Site.objects.get(name='localhost:8000'))
        sa.sites.add(Site.objects.get(name='transfer-guide.herokuapp.com'))
        sa.save()
