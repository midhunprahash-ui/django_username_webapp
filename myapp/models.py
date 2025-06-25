from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Employee(models.Model):
    emp_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manager_id = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    @property
    def employee_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.employee_name
