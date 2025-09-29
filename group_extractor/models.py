from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(unique=True)

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        # return self.phone_number
        return f"{self.phone_number} ({self.group.name})"

