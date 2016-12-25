from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from .cf_get import get_contest_info, CfApiError
from django.conf import settings

def base_response(request, body, title=None):
    context_dict = {"base_body": body}
    if title:
        context_dict["base_title"] = title
    return render(request, "base.html", context_dict)

def index(request):
    return render(request, "index.html", {})

def ldrbrd(request, contest_id=None):
    try:
        contest_id = int(contest_id or request.GET.get('contest'))
    except (TypeError, ValueError):
        raise Http404('Invalid Contest ID')
    try:
        show_unofficial = request.GET['show_unofficial'].lower() not in ('false', '0', '')
    except KeyError:
        show_unofficial = settings.SHOW_UNOFFICIAL

    usernames = User.objects.values_list('username', flat=True)

    contest, problems, participants = get_contest_info(contest_id, usernames, show_unofficial)

    context = {
        "contest_id": contest_id,
        "contest": contest,
        "problems": problems,
        "participants": participants,
    }
    return render(request, "ldrbrd.html", context)
