import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # needed for server rendering
import matplotlib.pyplot as plt

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

# ReportLab Imports for Professional PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .models import Dataset
from .serializers import DatasetSerializer

class UploadCSVView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file_obj = request.FILES['file']
        
        try:
            df = pd.read_csv(file_obj)
            
            # convert numpy types to python types for django
            total_records = int(len(df))
            
            avg_pressure = 0.0
            if 'Pressure' in df.columns:
                avg_pressure = float(df['Pressure'].mean())
                if np.isnan(avg_pressure): avg_pressure = 0.0
                
            avg_temp = 0.0
            if 'Temperature' in df.columns:
                avg_temp = float(df['Temperature'].mean())
                if np.isnan(avg_temp): avg_temp = 0.0

            type_dist = {}
            if 'Type' in df.columns:
                vc = df['Type'].value_counts()
                for k, v in vc.items():
                    type_dist[str(k)] = int(v)

            stats = {
                'total_records': total_records,
                'avg_pressure': round(avg_pressure, 2),
                'avg_temp': round(avg_temp, 2),
                'type_distribution': type_dist
            }

            dataset = Dataset.objects.create(file=file_obj, **stats)
            
            df['is_critical'] = (df['Pressure'] > 8.0) | (df['Temperature'] > 100)
            # clean up nan values before sending to frontend
            df_clean = df.head(50).where(pd.notnull(df), None)
            
            return Response({
                "stats": stats,
                "data": df_clean.to_dict(orient='records'),
                "history_id": dataset.id
            })

        except Exception as e:
            print(f"error uploading csv: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

class HistoryView(APIView):
    def get(self, request):
        try:
            datasets = Dataset.objects.order_by('-uploaded_at')[:5]
            serializer = DatasetSerializer(datasets, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"error fetching history: {e}")
            return Response({"error": str(e)}, status=500)
        
class GetDatasetView(APIView):
    def get(self, request, id):
        dataset = get_object_or_404(Dataset, pk=id)
        
        # read csv file to get actual table data
        try:
            df = pd.read_csv(dataset.file.path)
            df_clean = df.head(50).where(pd.notnull(df), None)
            rows = df_clean.to_dict(orient='records')
        except Exception:
            rows = []

        # build response with stats and data
        response_data = {
            "stats": {
                "total_records": dataset.total_records,
                "avg_pressure": dataset.avg_pressure,
                "avg_temp": dataset.avg_temp,
                "type_distribution": dataset.type_distribution
            },
            "data": rows,
            "history_id": dataset.id
        }
        return Response(response_data)
        
class DownloadPDFView(APIView):
    def get(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        file_path = dataset.file.path
        df = pd.read_csv(file_path)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()

        # header and title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=10,
            textColor=colors.HexColor('#0F766E'),
            alignment=1
        )
        elements.append(Paragraph("Chemical Analysis Report", title_style))
        elements.append(Paragraph(f"Dataset ID: #{dataset.id} | Generated via Chemical Visualizer", styles['Normal']))
        elements.append(Spacer(1, 20))

        # summary stats table
        summary_data = [
            ['Total Units', 'Avg Pressure (Bar)', 'Avg Temp (°C)'],
            [dataset.total_records, f"{dataset.avg_pressure:.2f}", f"{dataset.avg_pressure:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F766E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0FDFA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#0F766E')),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))

        # equipment distribution pie chart
        plt.figure(figsize=(6, 4))
        
        counts = df['Type'].value_counts()
        colors_list = ['#0F766E', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6']
        
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors_list[:len(counts)], startangle=140)
        plt.title('Equipment Type Distribution')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        img_buffer.seek(0)
        
        pdf_image = Image(img_buffer, width=400, height=250)
        elements.append(Paragraph("Equipment Distribution Analysis", styles['Heading2']))
        elements.append(pdf_image)
        elements.append(Spacer(1, 20))

        # detailed data table
        elements.append(Paragraph("Detailed Equipment Data (Top 50 Rows)", styles['Heading2']))
        
        table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        
        subset = df.head(50)
        
        # table styling
        table_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]

        # add data rows and highlight critical values
        for i, row in subset.iterrows():
            row_data = [
                row.get('Equipment Name', '-'),
                row.get('Type', '-'),
                row.get('Flowrate', 0),
                row.get('Pressure', 0),
                row.get('Temperature', 0)
            ]
            table_data.append(row_data)
            
            # mark critical readings in red
            try:
                p = float(row.get('Pressure', 0))
                t = float(row.get('Temperature', 0))
                if p > 8.0 or t > 100:
                    table_styles.append(('TEXTCOLOR', (0, i+1), (-1, i+1), colors.red))
                    table_styles.append(('FONTNAME', (0, i+1), (-1, i+1), 'Helvetica-Bold'))
            except:
                pass

        data_table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        data_table.setStyle(TableStyle(table_styles))
        
        elements.append(data_table)

        doc.build(elements)
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type='application/pdf')
    
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_400_BAD_REQUEST)