from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import PhishingTestForm
from .models import *
from django.shortcuts import get_object_or_404
from django.http import HttpResponse


def create_test(request):
    if request.method == 'POST':
        form = PhishingTestForm(request.POST)
        if form.is_valid():
            phishing_test = form.save()

            # Отправляем фишинговые письма всем сотрудникам
            employees = Employee.objects.all()
            for employee in employees:
                send_mail(
                    'Фишинговый тест',
                    'Это тест для проверки вашей устойчивости к фишингу.',
                    'admin@example.com',
                    [employee.email],
                )
            return redirect('test_list')
    else:
        form = PhishingTestForm()
    return render(request, 'phishing/create_test.html', {'form': form})


def track_action(request, test_id, employee_id, token):
    # Находим сотрудника и тест по переданным параметрам
    test = get_object_or_404(PhishingTest, id=test_id)
    employee = get_object_or_404(Employee, id=employee_id)

    # Фиксируем действие
    PhishingTestLog.objects.create(employee=employee, test=test, action='Clicked Link')

    # Например, перенаправляем сотрудника на страницу с сообщением
    return HttpResponse("Спасибо за участие в тестировании.")