from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.forms import EmailField


class Event(models.Model):
	event_name = models.CharField(max_length = 100)
	event_time = models.DateField()
	event_place = models.CharField(max_length = 100)
	potential_users = models.ManyToManyField(User)
	def __str__(self):
		return self.event_name

class Question(models.Model):
	question_text = models.CharField(max_length = 200)
	event = models.ForeignKey(Event, on_delete = models.CASCADE)
	editable = models.BooleanField(default=True)
	vendor_visible = models.BooleanField(default=True)
	freetext = models.BooleanField(default=False)
	def __str__(self):
		return self.event.event_name + "_" + self.question_text
	class Meta:
		ordering = ('question_text',)

class Choice(models.Model):
	choice_text = models.CharField(max_length = 100)
	votes = models.BigIntegerField(default = 0)
	question = models.ForeignKey(Question, on_delete = models.CASCADE)
	def __str__(self):
		return self.choice_text + "_" + self.question.__str__()
	class Meta:
		ordering = ('choice_text',)

class Response(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	choice = models.ForeignKey(Choice, on_delete = models.CASCADE)
	def __str__(self):
		return self.user.username + "_" + self.choice.__str__()

# class ResponseFreetext(models.Model):
# 	user = models.ForeignKey(User, on_delete = models.CASCADE)
# 	freetext = models.CharField(max_length = 500)
# 	question_id = models.BigIntegerField(default = 0)
# 	def __str__(self):
# 		return self.user.username + "_" + self.freetext.__str__()

class Permission(models.Model):
	# one event may correspond to many user statuses (at most 3), and one user status may correspond to many events
	event = models.ForeignKey(Event, on_delete = models.CASCADE)
	# one user may correspond to different statuses in different events, and one status may correspond to many users
	users = models.ManyToManyField(User)
	role = models.CharField(max_length = 10)
	def __str__(self):
		return self.role + "_" + self.event.__str__()
	

# invite guest, vendor, owner
class PermissionForm(ModelForm):
    class Meta:
        model = Permission
        fields = ['users', 'role']

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'event_time', 'event_place']

class QuestionForm(ModelForm):
	class Meta:
		model = Question
		fields = ['question_text', 'vendor_visible', 'freetext']

class ChoiceForm(ModelForm):
	class Meta:
		model = Choice
		fields = ['choice_text']

class MyUserCreationForm(UserCreationForm):
    email = EmailField(label="Email address", required=True,
        help_text="Required")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
