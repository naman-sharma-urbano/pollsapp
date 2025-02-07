from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import Question, Choice, Vote
from .serializers import QuestionSerializer, ChoiceSerializer, VoteSerializer,VotesSerializer, QuestionResultPageSerializer, UserSerializer
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404
# import json
@api_view(['GET'])
def userquestions(request):
	if request.method == 'GET':
		user = request.user
		questions = Question.objects.filter(owner=user, deleted=False)
		serializer = QuestionSerializer(questions, many=True)
		userqueryset = User.objects.all() 
		userset = UserSerializer(userqueryset, context={'request': request}, many=True)

		return Response(serializer.data)

@api_view(['GET'])
def todaysquestions_view(request):
	if request.method == 'GET':
		# return HttpResponse("Not Implemented")
		questions = Question.objects.filter(deleted=False)
		serializer = QuestionSerializer(questions, many=True)
		userqueryset = User.objects.all() 
		userset = UserSerializer(userqueryset, context={'request': request}, many=True)
		filtered_data = [item for item in serializer.data if item.get("was_published_recently") is not False]

		return Response(filtered_data)


@api_view(['GET', 'POST'])
def questions_view(request):
	if request.method == 'GET':
		question_id = request.query_params.get("question_id")
		status = request.query_params.get("status")
		question_text = request.query_params.get("question_text")
		pub_date = request.query_params.get("pub_date")
		sort_by = request.query_params.get("sort_by", "pub_date")
		sort_order = request.query_params.get("sort_order", "desc")
		questions = Question.objects.filter(deleted=False)
		if question_id:
			questions = questions.filter(id=question_id)
		if question_text:
			questions = questions.filter(question_text=question_text)
		if status:
			questions = questions.filter(status=status)
		if pub_date:
			questions = questions.filter(pub_date=pub_date)
		if sort_order == "asc":
			questions = questions.order_by(sort_by)
		else:
			questions = questions.order_by(f"-{sort_by}")

		serializer = QuestionSerializer(questions, many=True)
		userqueryset = User.objects.all() 
		userset = UserSerializer(userqueryset, context={'request': request}, many=True)

		return Response(serializer.data)
		# questions= []
		# for question in Question.objects.all():
		# 	question_representation = {'question_text': question.question_text, 'pub_date':question.pub_date.strftime("%Y-%m-%d")}
		# 	questions.append(question_representation)
		# return HttpResponse(json.dumps(questions), content_type='application/json')
	elif request.method == 'POST':
		serializer = QuestionSerializer(data=request.data)
		if serializer.is_valid():
			# question_text = serializer.data['question_text']
			# pub_date = serializer.data['pub_date']
			question = serializer.save()
			# Question.objects.create(**serializer.validated_data)
			return HttpResponse(QuestionSerializer(question), status=status.HTTP_201_CREATED)
		return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH', 'DELETE'])
def question_detail_view(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	if request.method == 'GET':
		serializer = QuestionSerializer(question)
		return Response(serializer.data)
	elif request.method == 'PATCH':
		serializer = QuestionSerializer(question,data=request.data, partial=True)
		if serializer.is_valid():
			question = serializer.save()
			return Response(QuestionSerializer(question).data)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
		# raise NotImplementedError("PATCH currently not supported")
	elif request.method == 'DELETE':
		question.deleted = True
		question.save()
		return Response("Question deleted",status=status.HTTP_204_NO_CONTENT)
		# raise NotImplementedError("DELETE currently not supported")

@api_view(['POST'])
def choices_view(request, question_id):
	question =get_object_or_404(Question, pk=question_id)
	serializer = ChoiceSerializer(data=request.data)
	if serializer.is_valid():
		choice = serializer.save(question=question)
		return Response(ChoiceSerializer(choice).data,  status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def vote_view(request, question_id):
	# import pdb
	# pdb.set_trace()
	question = get_object_or_404(Question, pk=question_id)
	serializer = VoteSerializer(data=request.data)
	question_data = QuestionSerializer(question)
	question_data = question_data.data
	if serializer.is_valid():
		choice = get_object_or_404(Choice, pk=serializer.validated_data['choice_id'], question=question)
		vote_type = serializer.validated_data['vote_type']

		if question_data['was_published_recently'] == False:
			return Response("Voting for this question is no longer available as the deadline has passed.")

		if question.status == "Close":
			return Response("Voting is close for this question")
		elif question.status == "Draft":
			return Response("Question is not published")

		if vote_type == "Upvote":
			if choice.votes >= 5:
				return Response("Choice not Available:Choice have max votes")
			else:
				votess =  Vote.objects.create(user= request.user, choice=choice, question=question, votes_type=serializer.validated_data['vote_type'])
				choice.votes += 1
				choice.save()
			return Response("UpVoted",status=status.HTTP_204_NO_CONTENT)
		elif vote_type == "Downvote":
			if choice.downvotes >= 5:
				return Response("Choice not Available:Choice have max votes")
			else:
				votess =  Vote.objects.create(user= request.user, choice=choice, question=question, votes_type=serializer.validated_data['vote_type'])
				choice.downvotes += 1
				choice.save()
			return Response("DownVoted",status=status.HTTP_204_NO_CONTENT)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def question_result_view(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	serializer = QuestionResultPageSerializer(question)

	return Response(serializer.data)