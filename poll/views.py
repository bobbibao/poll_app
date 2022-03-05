
from math import ceil
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, decorators
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .form import PollAddForm, EditPollForm, ChoiceAddForm
from .models import Poll, Choice, Vote, User
from django.db.models import Count
from django.contrib import messages
import re

# Create your views here.
# @login_required()

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.POST["profile"]
        print(profile)
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "form/re.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile != '':
                user.profile_pic = "profile_pic/" + profile
            else:
                user.profile_pic = "profile_pic/default-avatar.png"       
            user.save()
        except IntegrityError:
            return render(request, "form/re.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect('index')
    else:
        return render(request, "form/re.html")
def index(request):
    poll = 90
    return render(request, 'home/dashboard.html', {
        'poll':poll,
    })
class Login(View):
    def get(self, request):
        return render(request, 'form/login.html')
    def post(self, request):
        if request.method == 'POST':
            username = request.POST['your_name']
            password = request.POST['your_pass']
            user = authenticate(request, username = username, password = password)
            if user is None:
                return render(request, 'form/login.html', {
                    'message': 'Sai roi'
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))

def poll(request):
    if request.method == 'POST':
        form = PollAddForm(request.POST)
        if form.is_valid:
            poll = form.save(commit=False)
            poll.owner = request.user
            poll.save()
            new_choice1 = Choice(
                poll=poll, choice_text=form.cleaned_data['choice1']).save()
            new_choice2 = Choice(
                poll=poll, choice_text=form.cleaned_data['choice2']).save()

            messages.success(
                request, "Poll & Choices added successfully.", extra_tags='alert alert-success alert-dismissible fade show')

            return redirect('view')
    else:
        form = PollAddForm()
    context = {
        'form': form,
    }
    return render(request, 'home/polls.html', context)
class profile(View):
    def get(self, request, username):
        a = username
        user = User.objects.get(username=username)
        all_polls = Poll.objects.filter(owner=user)
        search_term = ''
        if 'name' in request.GET:
            all_polls = all_polls.order_by('text')

        if 'date' in request.GET:
            all_polls = all_polls.order_by('pub_date')

        if 'vote' in request.GET:
            all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')

        if 'search' in request.GET:
            search_term = request.GET['search']
            all_polls = all_polls.filter(text__icontains=search_term)

        paginator = Paginator(all_polls, 2)  # Show 6 contacts per page
        page = request.GET.get('page')
        polls = paginator.get_page(page)

        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
        print(ceil(paginator.count/2))
        pag = []
        for i in range(1,ceil(paginator.count/2)+1):
            pag.append(i)
        context = {
            'a': a,
            'user': user,
            'pag': pag,
            'polls': polls,
            'params': params,
            'search_term': search_term,
            
        }
        return render(request, 'home/profile.html', context)
def mobile(request): 
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if poll.active is False:
        if mobile(request):
            return render(request, 'home/result.html', {'poll': poll})
        return render(request, 'home/one.html', {'poll': poll})
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'home/poll_detail.html', context)
@decorators.login_required(login_url='/login/')
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this poll!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("view")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        messages.error(
            request, "Successfully!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("view")
    else:
        messages.error(
            request, "No choice selected!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("detail", poll_id)
    return render(request, 'home/view.html', {'poll': poll})

class result(View):
    def get(self, request, poll_id):
        poll = Poll.objects.get(pk=poll_id)
        return render(request, 'home/result.html', {
            'poll': poll,
        })
def end(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.active = False
    poll.save()
    return redirect("view")
def back(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.active = True
    poll.save()
    return redirect("view")
def view(request):
    all_polls = Poll.objects.all()
    search_term = ''
    if 'name' in request.GET:
        all_polls = all_polls.order_by('text')

    if 'date' in request.GET:
        all_polls = all_polls.order_by('pub_date')

    if 'vote' in request.GET:
        all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 2)  # Show 6 contacts per page
    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
    print(ceil(paginator.count/2))
    pag = []
    for i in range(1,ceil(paginator.count/2)+1):
        pag.append(i)
    context = {
        'pag': pag,
        'polls': polls,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'home/view.html', context)
def edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid:
            form.save()
            messages.success(request, "Poll Updated successfully.",
                             extra_tags='alert alert-success alert-dismissible fade show')
            return redirect("view")

    else:
        form = EditPollForm(instance=poll)

    return render(request, "home/edit.html", {'form': form, 'poll': poll})
@login_required
def delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('index')
    poll.delete()
    messages.success(request, "Poll Deleted successfully.",
                     extra_tags='alert alert-success alert-dismissible fade show')
    return redirect("view")

@login_required
def add(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('index')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'home/add.html', context)


@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('index')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'home/add_choice.html', context)
@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('index')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully.", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('edit', poll.id)

def error(request,*args, **argv):
    return render(request, 'home/error.html')

def search(request):
    users = User.objects.all()
    if 'search' in request.GET:
            search_term = request.GET['search']
            users = users.filter(first_name__icontains=search_term)
    total = []
    lst = []
    lst2 = []
    b = 0
    for i in users:
        a = Poll.objects.filter(owner=i)
        total.append(a.count())
        lst.append(i.first_name)
        lst2.append(i.last_name)
        b += 1

    print(lst)
    return render(request, 'home/user.html', {
        'users': users,
        'totals': total,
        'lst': lst,
        'lst2': lst2,
        'a': range(b),
    })