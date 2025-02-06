from rest_framework import serializers
from django.db import models
from .models import Question, Choice, Vote
from django.contrib.auth.models import User




class ChoiceSerializer(serializers.Serializer):
	choice_text =serializers.CharField(max_length=200)
	votes = serializers.IntegerField(read_only=True)
	downvotes = serializers.IntegerField(read_only=True)

	# voter = Vote.objects.filter(choice=Choice.objects)


	def create(self, validated_data):
		return Choice.objects.create(**validated_data)

class QuestionSerializer(serializers.Serializer):
	owner = serializers.ReadOnlyField(source='owner.username')
	# highlight = serializers.HyperlinkedIdentityField(view_name='questions-detail', format='html')
	question_text = serializers.CharField(max_length=200)
	pub_date = serializers.DateTimeField()
	was_published_recently = serializers.BooleanField(read_only=True)
	yesterday_published_question = serializers.BooleanField(read_only=True)
	verbose_question_text = serializers.CharField(read_only=True)
	choices = ChoiceSerializer(many=True, read_only=True)
	status = serializers.CharField(max_length=200)
	# DRF serializer.save() calls self.create(self.validated_data)
	def create(self, validated_data):
		return Question.objects.update(**validated_data)

	def update(self, instance, validated_data):
		for value in validated_data.items():
			setattr(instance, key, value)
		instance.save()
		return instance


	# def update(self, instance, validated_data):
	# 	instance.question = validated_data.get('question', instance.question)
	# 	instance.choice_text = validated_data.get('choice_text', instance.choice_text)
	# 	instance.votes = validated_data.get('votes', instance.votes)

	# 	instance.save()
	# 	return instance


class VoteSerializer(serializers.Serializer):
	choice_id = serializers.IntegerField()
	vote_type = serializers.CharField(max_length=200)

class ChoiceSerializerWithVotes(VoteSerializer):
	votes = serializers.IntegerField(read_only=True)

class QuestionResultPageSerializer(QuestionSerializer):
	choice = ChoiceSerializerWithVotes(many=True, read_only=True)
	# voters = Vote.objects.filter(question=Question, choice=choice)
	# votes = serializers.IntegerField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    # polls = serializers.HyperlinkedRelatedField(many=True, view_name='question-detail', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username']


class VotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'question', 'choice']