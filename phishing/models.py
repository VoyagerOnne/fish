from ckeditor.fields import RichTextField
from django.db import models
from django.utils.crypto import get_random_string
from django.template import Template, Context


class InterestTag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag


class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.CharField(max_length=255)
    tested = models.BooleanField(default=False)
    interests = models.ManyToManyField(InterestTag, related_name='employees', default=None)

    def __str__(self):
        return self.name


class PhishingTest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    employees = models.ManyToManyField(Employee, related_name='phishing_tests')

    def generate_unique_link(self, employee):
        unique_token = get_random_string(32)
        return f"127.0.0.1:8000/phishing_test/{self.id}/track/{employee.id}/{unique_token}/"

    def __str__(self):
        return self.name


class TestResult(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    phishing_test = models.ForeignKey(PhishingTest, on_delete=models.CASCADE)
    emails_sent = models.BooleanField(default=False)
    submitted_data = models.BooleanField(default=False)
    submitted_correct_data = models.BooleanField(default=False)
    opened_email = models.BooleanField(default=False)
    clicked_link = models.BooleanField(default=False)
    reported_email = models.BooleanField(default=False)
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.phishing_test}"


class PhishingEmailTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название шаблона ")
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = RichTextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    interests = models.ForeignKey(InterestTag, on_delete=models.CASCADE, default='None')


    def render_email(self, employee, test):
        """
        Метод для подстановки переменных в шаблон письма
        """
        context = {
            'user_name': employee.name,
            'user_email': employee.email,
            'unique_link': test.generate_unique_link(employee),
            'unique_link_p': "http://"+test.generate_unique_link(employee),
            'tracking_pixel_url': f"http://127.0.0.1:8000/phishing_test/{test.id}/track_open/{employee.id}/"
        }
        # Подставляем данные в шаблон через Template API Django
        return Template(self.body).render(Context(context)).replace('&nbsp;', '')

    def __str__(self):
        return self.name


class PhishingTestLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    test = models.ForeignKey(PhishingTest, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, default='Clicked Link')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} performed {self.action} on {self.test.name} at {self.timestamp}"