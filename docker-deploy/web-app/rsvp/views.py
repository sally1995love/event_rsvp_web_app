from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Question, Choice, Event, Permission, Response, PermissionForm, EventForm, QuestionForm, ChoiceForm, MyUserCreationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail

# class SignUp(generic.CreateView):
#     form_class = MyUserCreationForm
#     success_url = reverse_lazy('rsvp:home')
#     template_name = 'signup.html'
#     def form_valid(self, form):
#         self.object = form.save()
#         return super(SignUp, self).form_valid(form) 
def SignUp(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('rsvp:home'))
        else:
            return HttpResponseRedirect(reverse('rsvp:signup'))
    else:
        form = MyUserCreationForm()
        return render(request, 'signup.html', {'form':form})
    

class EventOwnerView(generic.ListView):
    model = User
    template_name = 'rsvp/event_owner.html'

class EventVendorView(generic.ListView):
    model = User
    template_name = 'rsvp/event_vendor.html'

class EventGuestView(generic.ListView):
    model = User
    template_name = 'rsvp/event_guest.html'

class EventOwnerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    template_name = 'rsvp/event_owner_detail.html'

class EventVendorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    template_name = 'rsvp/event_vendor_detail.html'

def event_guest_detail(request, pk):
    event = Event.objects.get(id = pk)
    responses = Response.objects.filter(user = request.user, choice__question__event = event)
    # questions = [ r.choice.question for r in responses ]
    all_questions = event.question_set.all()
    answered_questions = [r.choice.question for r in responses]
    unanswered_questions = [q for q in all_questions if q not in answered_questions]
    # elem for elem in li if len(elem) > 1
    return render(request, 'rsvp/event_guest_detail.html', {'responses':responses,'unanswered':unanswered_questions})

def question_delete(request, question_id):
    question = Question.objects.get(id = question_id)
    question.delete()
    event = question.event
    return HttpResponseRedirect(reverse('rsvp:event_owner_detail', args=(event.id,)))

def choice_delete(request, choice_id):
    choice = Choice.objects.get(id = choice_id)
    choice.delete()
    event = choice.question.event
    return HttpResponseRedirect(reverse('rsvp:event_owner_detail', args=(event.id,))) 

def permission_create(request, event_id):
    users = User.objects.all()
    event = Event.objects.get(id = event_id)
    form = PermissionForm(request.POST or None)
    if form.is_valid():
        for u in form.cleaned_data['users']:
            if form.cleaned_data['role'] == 'guest':
                event.potential_users.add(u)
                event.save()
            elif form.cleaned_data['role'] == 'vendor':
                perm = event.permission_set.get(role = 'vendor')
                perm.users.add(u)
            else:
                perm = event.permission_set.get(role = 'owner')
                perm.users.add(u)
        return render(request, 'rsvp/finish_create_event.html', {'event': event})
    return render(request, 'rsvp/permission_create.html', {'form': form, 'users': users})

def event_create(request, user_id):
    if request.method == 'POST':
        form = EventForm(request.POST)
        e = form.save();
        p_owner = Permission.objects.create(event=e, role='owner')
        p_owner.save()
        p_owner.users.add(User.objects.get(id = user_id))
        p_vendor = Permission.objects.create(event=e, role='vendor')
        p_vendor.save()
        p_guest = Permission.objects.create(event=e, role='guest')
        p_guest.save()
        return HttpResponseRedirect(reverse('rsvp:question_create_index', args=(e.id,)))
    else:
        form = EventForm()
        return render(request, 'rsvp/event_create.html', {'form': form})

def question_create(request, event_id):
    e = Event.objects.get(id=event_id)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':    
        q = Question.objects.create(event = e)
        form = QuestionForm(request.POST, instance=q)        
        form.save()
        # after finishing question edit, go to choice creation
        if not q.freetext:
            return HttpResponseRedirect(reverse('rsvp:choice_create_index', args=(q.id,)))
        else:
            return HttpResponseRedirect(reverse('rsvp:question_create_index', args=(e.id,)))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = QuestionForm()
        return render(request, 'rsvp/question_create.html', {'form': form})

def notify_question(request, event_id):
    e = Event.objects.get(id=event_id)
    to_email = []
    from_email = request.user.email
    subject = "You got some questions to answer for " + e.event_name
    contact_msg = "Go login your account to answer the new questions!"
    msg='<a href="http://vcm-151.vm.duke.edu:8080/rsvp/accounts/login" target="_blank">Join</a>'
    p = e.permission_set.get(role="guest")
    for user in p.users.all():
        to_email.append(user.email)
    # send to request change choice
    send_mail(subject, contact_msg, from_email, to_email, fail_silently=False, html_message=msg,)
    # return render(request, 'event_owner_detail.html', {'event':e})
    return HttpResponseRedirect(reverse('rsvp:event_owner_detail', args=(e.id,)))

def notify_choice(request, choice_id):
    # q = Question.objects.get(id=question_id)
    choice = Choice.objects.get(id = choice_id)
    choices = choice.question.choice_set.all()
    e = choice.question.event
    to_email = []
    from_email = request.user.email
    subject = "You got some new choices in question " + q.question_text + " for " + e.event_name
    contact_msg = "Go login your account to answer the new questions!"
    msg='<a href="http://vcm-151.vm.duke.edu:8080/rsvp/accounts/login" target="_blank">Join</a>'
    # p = e.permission_set.get(role="guest")
    # for user in p.users.all():
    #     to_email.append(user.email)
    to_email = [r.user for r in choice.response_set.all()]

    # send to request change choice
    send_mail(subject, contact_msg, from_email, to_email, fail_silently=False, html_message=mag,)
    # return render(request, 'event_owner_detail.html', {'event':e})
    return render(request, 'rsvp/choice_create_index.html', {'choices': choices, 'q': q})

def choice_create(request, question_id):
    q = Question.objects.get(id=question_id)
    event_id = q.event.id
    if request.method == 'POST':
        c = Choice.objects.create(question = q)
        form = ChoiceForm(request.POST, instance=c)
        form.save()
        return HttpResponseRedirect(reverse('rsvp:choice_create_index', args=(question_id,)))
    else:
        form = ChoiceForm()
        return render(request, 'rsvp/choice_create.html', {'form':form})

def choice_create_index(request, question_id):
    q = Question.objects.get(id=question_id)
    c = Choice.objects.filter(question = q)
    return render(request, 'rsvp/choice_create_index.html', {'choices': c, 'q':q})

def question_create_index(request, event_id):
    e = Event.objects.get(id=event_id)
    q = Question.objects.filter(event = e)
    return render(request, 'rsvp/question_create_index.html', {'questions': q, 'event':e})

def question_revise(request, question_id):
    q = Question.objects.get(id = question_id)
    event_id = q.event.id
    form = QuestionForm(request.POST or None, instance=q)        
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('rsvp:event_owner_detail', args=(event_id,)))
    return render(request, 'rsvp/question_revise.html', {'form': form})

def choice_revise(request, choice_id):
    c = Choice.objects.get(id = choice_id)
    event_id = c.question.event.id
    form = ChoiceForm(request.POST or None, instance=c)
    if form.is_valid():
        form.save()
        to_email = []
        from_email = request.user.email
        subject = "Choices of " + c.question.question_text + " has been changed!"
        contact_msg = "Go login your account to make new choices!"
        msg='<a href="http://vcm-151.vm.duke.edu:8080/rsvp/accounts/login" target="_blank">Join</a>'
        for r in c.response_set.all():
            to_email.append(r.user.email)
            # send to request change choice
            send_mail(subject, contact_msg, from_email, to_email, fail_silently=False, html_message=msg,)
        return HttpResponseRedirect(reverse('rsvp:event_owner_detail', args=(event_id,)))
    return render(request, 'rsvp/choice_revise.html', {'form':form})

@login_required
def guest_answer_index(request, permission_id):
    p = Permission.objects.get(id=permission_id)
    # register event
    if request.method == 'POST':
        p.users.add(request.user)
        p.event.potential_users.remove(request.user)
        return render(request, 'rsvp/finish_register_event.html')
        # should change to redirect
    else:
        event = p.event
        all_questions = Question.objects.filter(event = event)
        responses = Response.objects.filter(user = request.user, choice__question__event = event)
        answered = [r.choice.question for r in responses]
        unanswered = [q for q in all_questions if q not in answered]
        return render(request, 'rsvp/guest_answer_index.html', {'unanswered': unanswered,
            'answered':answered,'e':event, 'permission':p,
            'responses':responses})

# when guest are going to register event, answer question
@login_required
def guest_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    event = question.event
    permission = event.permission_set.get(role = "guest")
    freetext = question.freetext
    if request.method == 'POST':
        if not freetext:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
            selected_choice.votes += 1
            selected_choice.save()
            Response.objects.create(user = request.user, choice = selected_choice)
        else:
            new_choice = Choice.objects.create(question=question, 
                choice_text = request.POST.get('free_text'))
            Response.objects.create(user = request.user, choice = new_choice)           
        return HttpResponseRedirect(reverse('rsvp:guest_answer_index', args=(permission.id,)))
    else:
        return render(request, 'rsvp/guest_answer.html', {'question':question, 'freetext':freetext})

@login_required
def guest_answer_new(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    event = question.event
    permission = event.permission_set.get(role = "guest")
    freetext = question.freetext
    if request.method == 'POST':
        if not freetext:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
            selected_choice.votes += 1
            selected_choice.save()
            Response.objects.create(user = request.user, choice = selected_choice)
        else:
            new_choice = Choice.objects.create(question=question, 
                choice_text = request.POST.get('free_text'))
            Response.objects.create(user = request.user, choice = new_choice)           
        return HttpResponseRedirect(reverse('rsvp:event_guest_detail', args=(event.id,)))
    else:
        return render(request, 'rsvp/guest_answer.html', {'question':question, 'freetext':freetext})



# @login_required
# def guest_answer_new(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     event = question.event
#     permission = event.permission_set.get(role = "guest")
#     if request.method == 'POST':
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#         selected_choice.votes += 1
#         selected_choice.save()
#         Response.objects.create(user = request.user, choice = selected_choice)
#         return HttpResponseRedirect(reverse('rsvp:event_guest_detail', args=(event.id,)))
#     else:
#         return render(request, 'rsvp/guest_answer.html', {'question':question})

@login_required
def question_stop(request, question_id):
    question = get_object_or_404(Question, pk = question_id)
    question.editable = not question.editable
    question.save()
    event = question.event
    return HttpResponseRedirect(reverse('rsvp:event_vendor_detail', args=(event.id,)))

# when guest are going to revise question
def answer_revise(request, response_id):
    response = get_object_or_404(Response, pk=response_id)
    question = response.choice.question
    event = question.event
    permission = event.permission_set.get(role = "guest")
    freetext = question.freetext
    if request.method == 'POST':
        if not freetext:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
            selected_choice.votes += 1
            selected_choice.save()
            response.choice = selected_choice
            response.save()
        else:
            response.choice.choice_text = request.POST.get('free_text')
            response.choice.save()
        return HttpResponseRedirect(reverse('rsvp:event_guest_detail', args=(event.id,)))
    else:
        if not freetext:
            response.choice.votes -= 1
            response.choice.save()
        return render(request, 'rsvp/guest_answer.html', {'question':question, 'freetext':freetext})

# def vote(request, question_id, permission_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'rsvp/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse('rsvp:guest_answer_index', args=(permission_id,)))

# def detail(request, question_id, permission_id):
#     p = Permission.objects.get(id=permission_id)
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'rsvp/detail.html', {'question':question, 'permission':p,})

# display all the choices
# @login_required
# def guest_answer(request, question_id):
#     if request.method == 'POST':
#         Response.objects.create()
