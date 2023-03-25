import pandas as pd
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError(u'Type of file not CSV ! Only csv file can be uploaded !')


class TableFile(models.Model):
    file = models.FileField(upload_to='files/%Y/%m/%d/', validators=[validate_file_extension])

    def __init__(self, *args, **kwargs):
        super(TableFile, self).__init__(*args, **kwargs)
        print('TABLE FIE was CREATED')

    def __str__(self):
        return f'< File : {self.file.name} >'


class TableContent(models.Model):
    name = models.CharField(max_length=100, blank=True)
    columns = models.TextField(blank=True)
    rows = models.IntegerField(blank=True)
    file = models.ForeignKey(TableFile, on_delete=models.CASCADE, related_name='content', blank=False)

    def __init__(self, *args, **kwargs):
        super(TableContent, self).__init__(*args, **kwargs)

    def __str__(self):
        return f'< Table Content of : {self.name}   ' \
               f'Columns : {len(self.columns.split(","))}   ' \
               f'Rows : {self.rows} >'

    @staticmethod
    @receiver(post_save, sender=TableFile)
    def create_other_model(instance, created, **kwargs):
        if created:
            name = instance.file.name
            df = pd.read_csv(instance.file.path, encoding='utf-8')
            columns = df.columns[1:]
            rows = len(df.axes[0])
            content = TableContent.objects.create(
                name=name,
                columns=",".join(columns),
                rows=rows,
                file=instance,
            )
