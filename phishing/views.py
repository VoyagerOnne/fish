from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import AbstractUser
from django.utils.html import strip_tags

from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
import csv
from django.db.models import Count
import random
from django.core.mail import send_mail, EmailMultiAlternatives
from .forms import *


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        # Вход пользователя
        login(request, form.get_user())
        return redirect('home')  # Замените на ваш URL
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect('login')


class HomeView(ListView):
    model = AbstractUser
    template_name = 'index.html'
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        context['tests'] = PhishingTest.objects.filter(active=True)
        return context


# Функция для обработки текстового файла и создания сотрудников
def handle_uploaded_file(file, request):
    # Открываем файл в режиме чтения
    decoded_file = file.read().decode('Windows-1251')
    reader = csv.reader(decoded_file.splitlines())
    for row in reader:
        # В каждой строке должны быть имя, email и департамент
        name, email, department = row[0], row[1], row[2]
        # Если не указаны интересы, значение устанавливается в None
        interests = row[3:] if len(row) > 3 else []

        existing_interests = InterestTag.objects.filter(tag__in=interests)
        existing_interest_names = set(existing_interests.values_list('tag', flat=True))
        # Определяем, какие теги нужно создать
        missing_interests = set(interests) - existing_interest_names

        # Если есть недостающие теги, уведомляем пользователя
        if missing_interests:
            messages.warning(request, f"Следующие теги интересов отсутствуют: {', '.join(missing_interests)}")
            # Спрашиваем разрешение на создание тегов (можно обработать это в другой части кода)
            create_tags = True  # Можно заменить на форму с запросом разрешения
            if create_tags:
                for interest in missing_interests:
                    InterestTag.objects.create(tag=interest)

        employee = Employee.objects.create(name=name, email=email, department=department)

        if interests:
            employee_interests = InterestTag.objects.filter(tag__in=interests)
            employee.interests.add(*employee_interests)


# Представление для добавления сотрудника
@login_required
def add_employee(request):
    if request.method == 'POST':
        # Если пользователь добавляет сотрудника вручную
        if 'submit_manual' in request.POST:
            form = EmployeeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Сотрудник успешно добавлен.")
                return redirect('employee_list')
            if not form.is_valid():
                messages.error(request, f"Ошибка при добавлении сотрудника. Убедитесь, что все поля заполнены корректно. Все поля обязательны")
                return render(request, 'add_employee.html', {'form': form})
        # Если пользователь загружает файл
        elif 'submit_file' in request.POST:
            file_form = UploadFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                try:
                    handle_uploaded_file(request.FILES['file'], request)
                    messages.success(request, "Сотрудники успешно добавлен.")
                except UnicodeError:
                    messages.warning(request, f"Убедитесь в корректности загруженного файла. Расширение должно быть CSV")
                    return redirect('add_employee')
                except IndexError:
                    messages.warning(request, f"Загруженный файл не соответсвует формату: ФИО,Email,Департамент,Интересы")
                    return redirect('add_employee')
                except Exception as e:
                    messages.warning(request, f"Ошибка при загрузке файла: {e}")
                    return redirect('add_employee')
                return redirect('employee_list')
            if not file_form.is_valid():
                messages.error(request, "Ошибка при добавлении сотрудников. Убедитесь, что формат и тип файла соответствуют.")
                return redirect('add_employee')
    else:
        form = EmployeeForm()
        file_form = UploadFileForm()

    return render(request, 'add_employee.html', {
        'form': form,
        'file_form': file_form
    })


#
class EmployeeListView(ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context


# Удаление сотрудника
class EmployeeDeleteView(View):
    def post(self, request):
        employee_ids = request.POST.getlist('employees')  # Получаем список выбранных сотрудников
        if employee_ids:
            Employee.objects.filter(id__in=employee_ids).delete()
            messages.success(request, 'Сотрудник успешно удален.')
        else:
            messages.warning(request, 'Не выбрано ни одного сотрудника.')
        return redirect('employee_list')  # Укажите URL, куда перенаправить после удаления


# Представление для создания тестов
class PhishingTestCreateView(CreateView):
    model = PhishingTest
    form_class = PhishingTestForm
    template_name = 'add_test.html'
    success_url = reverse_lazy('created_tests')

    def form_valid(self, form):
        response = super().form_valid(form)
        employees = form.cleaned_data['employees']  # Получаем сотрудников из формы
        messages.success(self.request, f'Новое тестирование успешно создано')
        self.object.employees.set(employees)  # Привязываем сотрудников к тесту
        return response

    def form_invalid(self, form):
        messages.warning(self.request, f"Убедитесь в корректности введенных данных")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()  # Получаем всех сотрудников
        return context



# Представление для просмотра уже созданных тестов
class PhishingTestListView(ListView):
    model = PhishingTest
    template_name = 'created_tests.html'
    context_object_name = 'phishing_tests'
    ordering = ['-created_at']


# Представление для детального просмотра уже созданных тестов
class PhishingTestDetailView(DetailView):
    model = PhishingTest
    template_name = 'test_detail.html'
    context_object_name = 'test'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем список кортежей (сотрудник, ссылка)
        context['employee_links'] = [
            (employee, self.object.generate_unique_link(employee))
            for employee in self.object.employees.all()
        ]
        return context


# Удаление теста
class PhishingTestDeleteView(DeleteView):
    model = PhishingTest
    template_name = 'test_delete.html'  # Укажите имя вашего шаблона
    success_url = reverse_lazy('created_tests')  # Укажите URL, куда перенаправить после успешного удаления

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Тест успешно удален.')
        return super().form_valid(form)


class PhishingEmailTemplateCreateView(CreateView):
    model = PhishingEmailTemplate
    form_class = PhishingEmailTemplateForm
    template_name = 'create_email_template.html'
    success_url = reverse_lazy('email_template_list')

    def form_valid(self, form):
        messages.success(self.request, 'Шаблон успешно создан.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, f"Убедитесь в корректности введенных данных")
        return super().form_invalid(form)


class PhishingEmailTemplateListView(ListView):
    model = PhishingEmailTemplate
    template_name = 'email_templates_list.html'  # Шаблон для отображения списка шаблонов
    context_object_name = 'templates'


class PhishingEmailTemplateDetailView(DetailView):
    model = PhishingEmailTemplate
    template_name = 'email_template_detail.html'  # Шаблон для отображения одного шаблона
    context_object_name = 'template'


class PhishingEmailTemplateDeleteView(DeleteView):
    model = PhishingEmailTemplate
    template_name = 'email_template_delete.html'  # Укажите имя вашего шаблона
    success_url = reverse_lazy('email_templates_list')  # Укажите URL, куда перенаправить после успешного удаления

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Шаблон успешно удален.')
        return super().form_valid(form)


class PhishingEmailTemplateUpdateView(UpdateView):
    model = PhishingEmailTemplate
    form_class = PhishingEmailTemplateForm
    template_name = 'create_email_template.html'
    success_url = reverse_lazy('email_templates_list')

    def form_valid(self, form):
        messages.success(self.request, 'Шаблон успешно обновлен.')
        return super().form_valid(form)


from django.utils.html import strip_tags

def start_phishing_test(request, test_id):
    test = get_object_or_404(PhishingTest, id=test_id)
    if test.active:
        return JsonResponse({'status': 'error', 'message': 'Test is already active'})

    # Активируем тест
    test.active = True
    test.save()

    employees = test.employees.filter(tested=False)

    for employee in employees:
        # Найдем шаблон с учетом интересов сотрудника
        interest_tags = employee.interests.all()
        count = PhishingEmailTemplate.objects.filter(interests__in=interest_tags).count()
        if count > 0:
            email_template = PhishingEmailTemplate.objects.filter(interests__in=interest_tags)[random.randint(0, count - 1)]
        else:
            count = PhishingEmailTemplate.objects.all().count()
            email_template = PhishingEmailTemplate.objects.all()[random.randint(0, count - 1)]

        if email_template:
            # Генерируем тело письма на основе HTML-шаблона &nbsp
            email_body = email_template.render_email(employee, test)

            # Убираем HTML-теги для текстовой версии
            text_body = strip_tags(email_body)

            msg = EmailMultiAlternatives(
                subject=email_template.subject,
                body=text_body,  # Текстовая версия письма
                from_email='voyageronne@gmail.com',
                to=[employee.email],
            )

            msg.attach_alternative(email_body, "text/html")

            msg.extra_headers = {
                'MIME-Version': '1.0',
                'Content-Type': 'text/html; charset=UTF-8',
            }

            msg.send(fail_silently=False)

            # Логируем отправку
            PhishingTestLog.objects.create(employee=employee, test=test, action='Email Sent')

    messages.info(request, 'Test Started')

    return redirect(reverse('test_detail', args=[test.id]))



def stop_phishing_test(request, test_id):
    test = get_object_or_404(PhishingTest, id=test_id)
    if not test.active:
        return JsonResponse({'status': 'error', 'message': 'Test is not active'})

    # Останавливаем тест
    test.active = False
    test.save()

    messages.info(request, 'Test Stopped')

    return redirect(reverse('test_detail', args=[test.id]))


def track_link(request, test_id, employee_id, token):
    test = get_object_or_404(PhishingTest, id=test_id)
    employee = get_object_or_404(Employee, id=employee_id)


    TestResult.objects.update_or_create(
        employee=employee,
        phishing_test=test,
        clicked_link=True
    )
    PhishingTestLog.objects.create(
        employee=employee,
        test=test,
        action='Clicked Link'
    )

    # Перенаправляем на какую-то страницу (например, фейковую страницу входа)
    return HttpResponseRedirect(reverse('fake_login_page', args=[test.id, employee.id]))


def fake_login_page(request, test_id, employee_id):
    test = get_object_or_404(PhishingTest, id=test_id)
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = FakeLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Журналируем ввод данных
            if email == employee.email:
                PhishingTestLog.objects.create(
                    employee=employee,
                    test=test,
                    action='Entered real email'
                )
                TestResult.objects.filter(employee=employee, phishing_test=test).update(
                    submitted_correct_data=True
                )
                messages.info(request, "Добавлено одно новое событие в тесте " + test.name)
            else:
                PhishingTestLog.objects.create(
                    employee=employee,
                    test=test,
                    action='Entered fake email'
                )
                TestResult.objects.filter(employee=employee, phishing_test=test).update(
                    submitted_data=True
                )
                messages.info(request, "Добавлено одно новое событие в тесте " + test.name)

            return HttpResponse(status=403)  # Перенаправляем на страницу благодарности

    else:
        form = FakeLoginForm()

    return render(request, 'fake_login_page.html', {'form': form})


def campaign_results_view(request, test_id):
    phishing_test = get_object_or_404(PhishingTest, id=test_id)
    test_results = TestResult.objects.filter(phishing_test=phishing_test)

    # Подсчёт ключевых метрик
    total_emails_sent = test_results.count()
    total_clicked_link = test_results.filter(clicked_link=True).count()
    total_submitted_data = test_results.filter(submitted_data=True).count()
    total_submitted_correct_data = test_results.filter(submitted_correct_data=True).count()

    context = {
        'phishing_test': phishing_test,
        'test_results': test_results,
        'total_emails_sent': total_emails_sent,
        'total_clicked_link': total_clicked_link,
        'total_submitted_data': total_submitted_data,
        'total_submitted_correct_data': total_submitted_correct_data,
    }

    return render(request, 'campaign_results.html', context)


def export_csv(request, test_id):
    phishing_test = get_object_or_404(PhishingTest, id=test_id)
    test_results = TestResult.objects.filter(phishing_test=phishing_test)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{phishing_test.name}_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee Name', 'Email', 'Clicked Link', 'Submitted Data', 'Submitted Correct Data'])

    for result in test_results:
        writer.writerow([
            result.employee.name,
            result.employee.email,
            result.clicked_link,
            result.submitted_data,
            result.submitted_correct_data
        ])

    return response


def track_open_email(request, test_id, employee_id):
    test = get_object_or_404(PhishingTest, id=test_id)
    employee = get_object_or_404(Employee, id=employee_id)

    # Логируем открытие письма
    TestResult.objects.create(
        employee=employee,
        phishing_test=test,
        opened_email=True
    )

    PhishingTestLog.objects.create(
        employee=employee,
        test=test,
        action='Opened Email'
    )

    # Возвращаем 1x1 пиксельное изображение
    return HttpResponse(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\xff\x00\xc0\xc0\xc0\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b', content_type='image/gif')