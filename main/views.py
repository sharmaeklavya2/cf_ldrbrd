from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from .cf_get import get_contest_info, get_user_info, CfApiError
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

def add_users(request):
    if not settings.SHOW_ADD_USERS_PAGE:
        raise Http404('add_users page has been disabled')
    context = {}
    if request.method == 'POST':
        if "usernames" in request.POST and request.POST["usernames"]:
            usernames = request.POST["usernames"]
            try:
                cf_users = get_user_info([usernames])
            except CfApiError as e:
                message = e.response.json()['comment']
                if message.startswith("handles: "):
                    message = message[len("handles: "):]
                context["error"] = message
            else:
                new_users = []
                updated_users = []
                for cf_user in cf_users:
                    try:
                        user = User.objects.get(username=cf_user.username)
                        user.first_name = cf_user.first_name
                        user.last_name = cf_user.last_name
                        user.save()
                        updated_users.append(cf_user.username)
                    except User.DoesNotExist:
                        User.objects.create_user(cf_user.username, first_name=cf_user.first_name, last_name=cf_user.last_name)
                        new_users.append(cf_user.username)
                if new_users:
                    plural = 's' if len(new_users) > 1 else ''
                    context["add_success"] = "Successfully added user{} {}.".format(plural, ", ".join(new_users))
                if updated_users:
                    plural = 's' if len(updated_users) > 1 else ''
                    context["update_success"] = "Successfully updated user{} {}.".format(plural, ", ".join(updated_users))
        else:
            context["error"] = "Usernames field cannot be empty."
    return render(request, "add_users.html", context)
