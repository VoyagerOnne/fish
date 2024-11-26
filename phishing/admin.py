from django.contrib import admin
from .models import *


admin.site.register(InterestTag)
admin.site.register(Employee)
admin.site.register(PhishingEmailTemplate)
admin.site.register(TestResult)
admin.site.register(PhishingTestLog)
admin.site.register(PhishingTest)