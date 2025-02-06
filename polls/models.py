import datetime
from django.db import models
from django.conf import settings  # Correct way to reference the User model

from django.utils import timezone

from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from pygments.lexers import PythonLexer
from django.utils.html import escape
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField()
	owner = models.ForeignKey('auth.User', related_name='question', on_delete=models.CASCADE, default=1)
	status = models.CharField(max_length=15,
        choices=[
            ("Open", "Open"),
            ("Close", "Close"),
            ("Draft", "Draft"),
        ],
        default="Open",
    )
	deleted = models.BooleanField(default=False)
	# highlighted = models.TextField(blank=True, null=True)  # Ensure the field exists
	def __str__(self):
		return self.question_text
	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.pub_date <= now
	def yesterday_published_question(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1)
	def verbose_question_text(self):
		return "Question : %s" % (self.question_text)
	def choices(self):
		if not hasattr(self, '_choices'):
			self._choices = self.choice_set.all()
		return self._choices
	# Auth and permission
	def save(self, *args, **kwargs):
		if self.question_text:
			formatter = HtmlFormatter(full=True)
			self.highlighted = highlight(escape(self.question_text), PythonLexer(), formatter)
		super().save(*args, **kwargs)

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)
	downvotes = models.IntegerField(default=0)
	owner = models.ForeignKey('auth.User', related_name='choice', on_delete=models.CASCADE, default=1)
	# highlighted = models.TextField()
	def __str__(self):
		return self.choice_text

class Vote(models.Model):
	# user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow NULL users

	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
	votes_type = models.CharField(max_length=200,
		choices=[
            ("Upvote", "Upvote"),
            ("Downvote", "Downvote"),
        ],
        default= "Upvote")

	def __str__(self):
		return f"Vote on ({self.question})({self.choice}) by User({self.user.id})"


