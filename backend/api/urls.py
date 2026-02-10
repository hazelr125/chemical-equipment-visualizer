from django.urls import path
from .views import UploadCSVView, HistoryView, DownloadPDFView, login_view, GetDatasetView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:dataset_id>/', DownloadPDFView.as_view(), name='report'),
    path('login/', login_view, name='login'),
    path('history/<int:id>/', GetDatasetView.as_view(), name='get_dataset'),
]
