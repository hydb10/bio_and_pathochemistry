from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Quiz, Question, Choice, Result
import random

def quiz_list(request):
    bio_quizzes = Quiz.objects.filter(category='bio')
    patho_quizzes = Quiz.objects.filter(category='patho')

    return render(request, 'quiz/quiz_list.html', {
        'bio_quizzes': bio_quizzes,
        'patho_quizzes': patho_quizzes,
    })

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    questions_list = list(quiz.questions.all())
    random.shuffle(questions_list) 
    
    question_ids = [q.id for q in questions_list]
    request.session[f'quiz_{quiz_id}_question_order'] = question_ids
    
    if not questions_list:
        messages.warning(request, 'В этой викторине пока нет вопросов')
        return redirect('quiz_list')
    
    first_question = questions_list[0]
    
    request.session[f'quiz_{quiz_id}_answers'] = {}
    request.session[f'quiz_{quiz_id}_current'] = first_question.id
    
    return redirect('question_view', quiz_id=quiz_id, question_id=first_question.id)

def question_view(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    question_order = request.session.get(f'quiz_{quiz_id}_question_order', [])
    
    if not question_order:
        questions_list = list(quiz.questions.all())
        random.shuffle(questions_list)
        question_order = [q.id for q in questions_list]
        request.session[f'quiz_{quiz_id}_question_order'] = question_order
    
    if request.method == 'POST':
        selected_choice_id = request.POST.get('choice')
        if selected_choice_id:
            answers = request.session.get(f'quiz_{quiz_id}_answers', {})
            answers[str(question_id)] = int(selected_choice_id)
            request.session[f'quiz_{quiz_id}_answers'] = answers
            
            current_index = question_order.index(question_id)
            
            if current_index + 1 < len(question_order):
                next_question_id = question_order[current_index + 1]
                return redirect('question_view', quiz_id=quiz_id, question_id=next_question_id)
            else:
                if f'quiz_{quiz_id}_question_order' in request.session:
                    del request.session[f'quiz_{quiz_id}_question_order']
                return redirect('result_view', quiz_id=quiz_id)
    
    choices = question.choices.all()
    
    current_number = question_order.index(question_id) + 1
    total_questions = len(question_order)
    
    return render(request, 'quiz/question.html', {
        'quiz': quiz,
        'question': question,
        'choices': choices,
        'current_number': current_number,
        'total_questions': total_questions,
    })

def result_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    answers = request.session.get(f'quiz_{quiz_id}_answers', {})
    
    correct_count = 0
    total_count = quiz.questions.count()
    results = []
    
    for question in quiz.questions.all():
        user_choice_id = answers.get(str(question.id))
        correct_choice = question.choices.filter(is_correct=True).first()
        is_correct = False
        user_choice_text = None
        
        if user_choice_id:
            user_choice = question.choices.filter(id=user_choice_id).first()
            user_choice_text = user_choice.text if user_choice else None
            is_correct = user_choice and user_choice.is_correct
            if is_correct:
                correct_count += 1
        
        results.append({
            'question': question,
            'user_choice': user_choice_text,
            'correct_choice': correct_choice.text if correct_choice else None,
            'is_correct': is_correct,
            'explanation': question.explanation,
        })
    
    percentage = (correct_count / total_count * 100) if total_count > 0 else 0
    
    # Очищаем сессию
    if f'quiz_{quiz_id}_answers' in request.session:
        del request.session[f'quiz_{quiz_id}_answers']
    
    from .models import Result

    if request.user.is_authenticated:
        Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=correct_count,
            total=total_count,
            answers_data=answers
        )

    return render(request, 'quiz/result.html', {
        'quiz': quiz,
        'results': results,
        'correct_count': correct_count,
        'total_count': total_count,
        'percentage': percentage,
    })

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            return render(request, 'quiz/register.html', {'error': 'Ник уже занят'})

        user = User.objects.create_user(username=username)
        login(request, user)
        return redirect('quiz_list')

    return render(request, 'quiz/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('quiz_list')
        except User.DoesNotExist:
            return render(request, 'quiz/login.html', {'error': 'Пользователь не найден'})

    return render(request, 'quiz/login.html')


def logout_view(request):
    logout(request)
    return redirect('quiz_list')

def stats_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    results = Result.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'quiz/stats.html', {'results': results})

def result_detail(request, result_id):
    result = get_object_or_404(Result, id=result_id, user=request.user)
    quiz = result.quiz
    answers = result.answers_data or {}

    results = []

    for question in quiz.questions.all():
        user_choice_id = answers.get(str(question.id))
        correct_choice = question.choices.filter(is_correct=True).first()

        user_choice = None
        if user_choice_id:
            user_choice = question.choices.filter(id=user_choice_id).first()

        results.append({
            'question': question,
            'user_choice': user_choice.text if user_choice else None,
            'correct_choice': correct_choice.text if correct_choice else None,
            'is_correct': user_choice and user_choice.is_correct,
            'explanation': question.explanation,
        })

    return render(request, 'quiz/result.html', {
        'quiz': quiz,
        'results': results,
        'correct_count': result.score,
        'total_count': result.total,
        'percentage': (result.score / result.total * 100) if result.total else 0,
    })