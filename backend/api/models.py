from django.db import models

class Dataset(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='csvs/')
    # stats from uploaded csv
    total_records = models.IntegerField(default=0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temp = models.FloatField(default=0.0)
    type_distribution = models.JSONField(default=dict)

    def __str__(self):
        return f"Dataset {self.id} - {self.uploaded_at.strftime('%H:%M:%S')}"