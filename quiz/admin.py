from django.contrib import admin
from .models import Quiz, Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    inlines = [QuestionInline]

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Изображение'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'order', 'has_image']
    list_filter = ['quiz']
    inlines = [ChoiceInline]
    fields = ['quiz', 'text', 'explanation', 'order', 'image']

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = 'Изображение'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_editable = ['is_correct']