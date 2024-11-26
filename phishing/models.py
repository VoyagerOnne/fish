from django.db import models
from django.utils.crypto import get_random_string


class InterestTag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag


class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.CharField(max_length=255)
    tested = models.BooleanField(default=False)
    interests = models.ForeignKey(InterestTag, related_name='interests', on_delete=models.CASCADE, default='None')

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
        return f"/phishing_test/{self.id}/track/{employee.id}/{unique_token}/"

    def __str__(self):
        return self.name


class TestResult(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    phishing_test = models.ForeignKey(PhishingTest, on_delete=models.CASCADE)
    opened_email = models.BooleanField(default=False)
    clicked_link = models.BooleanField(default=False)
    reported_email = models.BooleanField(default=False)
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.phishing_test}"


class PhishingEmailTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название шаблона ")
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    interests = models.ForeignKey(InterestTag, on_delete=models.CASCADE, default='None')

    def __str__(self):
        return self.name


class PhishingEmail(models.Model):
    phishing_test = models.ForeignKey(PhishingTest, on_delete=models.CASCADE)
    template = models.ForeignKey(PhishingEmailTemplate, on_delete=models.CASCADE)
    interest_tags = models.ManyToManyField(InterestTag, related_name='phishing_emails')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phishing_test} - {self.template}"


class PhishingTestLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    test = models.ForeignKey(PhishingTest, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, default='Clicked Link')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} performed {self.action} on {self.test.name} at {self.timestamp}"
