from django.db import models

class Quiz(models.Model):
    CATEGORY_CHOICES = [
        ('bio', 'Тренажеры по биохимии'),
        ('patho', 'Тренажеры по патохимии'),
    ]

    title = models.CharField('Название викторины', max_length=200)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    category = models.CharField(
        'Раздел',
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='bio'
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Викторина'
        verbose_name_plural = 'Викторины'

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='Викторина')
    text = models.CharField('Текст вопроса', max_length=2000)
    explanation = models.TextField('Пояснение', blank=True)
    order = models.IntegerField('Порядок', default=0)
    
    image = models.ImageField('Изображение к вопросу', upload_to='question_images/', blank=True, null=True)
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=1000)
    is_correct = models.BooleanField('Правильный ответ', default=False)
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

from django.contrib.auth.models import User

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    answers_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
