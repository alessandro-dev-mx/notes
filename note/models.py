from django.db import models, transaction


class Category(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Note(models.Model):
    COLORS = (
        ('Gray', 'Gray'),
        ('Red', 'Red'),
        ('Orange', 'Orange'),
        ('Yellow', 'Yellow'),
    )
    NOTE_TYPE = (
        ('Note', 'Note'),
        ('List', 'List'),
    )
    title = models.CharField(max_length=120)
    content = models.TextField(blank=True, null=True)
    note_type = models.CharField(
        max_length=24, default=NOTE_TYPE[0][0], choices=NOTE_TYPE, blank=True)
    category = models.ForeignKey(
        Category, default=1, on_delete=models.CASCADE, blank=True)
    color = models.CharField(max_length=24, null=True,
                             choices=COLORS, blank=True)
    pinned = models.BooleanField(default=False)
    reminder = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
