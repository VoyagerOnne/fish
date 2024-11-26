from django.contrib import admin
from .models import *


admin.site.register(InterestTag)
admin.site.register(Employee)
admin.site.register(PhishingTest)
admin.site.register(TestResult)
admin.site.register(PhishingEmail)
admin.site.register(PhishingEmailTemplate)
admin.site.register(PhishingTestLog)