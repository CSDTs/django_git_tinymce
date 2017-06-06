from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True, primary_key=True)
    description = models.CharField(max_length=200)
    create_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
class Owner(models.Model):
    repo = models.ForeignKey(Repository)