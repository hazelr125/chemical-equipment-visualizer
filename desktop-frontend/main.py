import sys
import requests
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QFileDialog, QHBoxLayout, QFrame, 
                             QMessageBox, QDialog, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# api endpoint
API_URL = "http://127.0.0.1:8000/api/"

# app styling
STYLESHEET = """
QMainWindow { background-color: #F8F9FA; }
QLabel { font-family: 'Segoe UI'; color: #334155; }
QPushButton {
    background-color: #0F766E; color: white; border-radius: 6px;
    padding: 10px 20px; font-weight: bold; font-size: 14px; border: none;
    text-align: left;
}
QPushButton:hover { background-color: #115E59; }
QFrame#Card { background-color: white; border-radius: 10px; border: 1px solid #E2E8F0; }
QDialog { background-color: white; }
QLineEdit { padding: 8px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 14px; }
QTableWidget { 
    background-color: white; border: 1px solid #E2E8F0; border-radius: 6px; 
    gridline-color: #F1F5F9; font-family: 'Segoe UI';
}
QHeaderView::section {
    background-color: #F8FAFC; padding: 8px; border: none; 
    font-weight: bold; color: #64748B;
}
"""

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(QIcon('assets/logo.png'))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        # welcome header
        title_layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap('assets/user.png')
        if not pixmap.isNull():
             icon_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        text_layout = QVBoxLayout()
        lbl_welcome = QLabel("Welcome Back")
        lbl_welcome.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F766E;")
        lbl_sub = QLabel("Sign in to continue")
        lbl_sub.setStyleSheet("font-size: 12px; color: #94A3B8;")
        
        text_layout.addWidget(lbl_welcome)
        text_layout.addWidget(lbl_sub)

        title_layout.addWidget(icon_label)
        title_layout.addLayout(text_layout)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # login fields
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.btn_login = QPushButton("Sign In")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.accept)
        self.btn_login.setStyleSheet("background-color: #0F766E; color: white; border-radius: 6px; padding: 10px; text-align: center;")
        layout.addWidget(self.btn_login)

    def get_credentials(self):
        return self.username.text(), self.password.text()

class ChemicalVisualizerDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Visualizer")
        self.setGeometry(100, 100, 1200, 850)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(QIcon('assets/logo.png'))
        
        self.current_id = None
        self.token = None
        self.stats_labels = {}
        
        # authenticate user
        if self.perform_login():
             self.init_ui()
        else:
             sys.exit() 

    def perform_login(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            try:
                response = requests.post(API_URL + "login/", json={'username': username, 'password': password})
                if response.status_code == 200:
                    self.token = response.json()['token']
                    return True
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid Credentials")
                    return False
            except:
                QMessageBox.critical(self, "Error", "Cannot connect to server. Is it running?")
                return False
        return False

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # top header bar
        header_layout = QHBoxLayout()
        
        title_container = QHBoxLayout()
        logo_label = QLabel()
        pixmap = QPixmap('assets/logo.png')
        if not pixmap.isNull():
             logo_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title = QLabel("Chemical Parameter Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-left: 10px;")
        
        title_container.addWidget(logo_label)
        title_container.addWidget(title)
        title_container.addStretch()

        # action buttons
        self.btn_pdf = QPushButton("  Download Report")
        self.btn_pdf.setIcon(QIcon('assets/pdf.png'))
        self.btn_pdf.setIconSize(QSize(20, 20))
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.download_pdf)
        self.btn_pdf.setStyleSheet("background-color: #475569; text-align: left; padding-left: 15px;")
        
        self.btn_upload = QPushButton("  Upload CSV")
        self.btn_upload.setIcon(QIcon('assets/upload.png'))
        self.btn_upload.setIconSize(QSize(20, 20))
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.clicked.connect(self.upload_file)
        self.btn_upload.setStyleSheet("background-color: #0F766E; text-align: left; padding-left: 15px;")

        header_layout.addLayout(title_container)
        header_layout.addWidget(self.btn_pdf)
        header_layout.addWidget(self.btn_upload)
        main_layout.addLayout(header_layout)

        # kpi cards
        stats_container = QHBoxLayout()
        self.card_pressure = self.create_stat_card("Avg Pressure", "-- Bar", "assets/pressure.png")
        self.card_temp = self.create_stat_card("Avg Temp", "-- °C", "assets/temperature.png")
        self.card_count = self.create_stat_card("Total Units", "--", "assets/units.png")
        
        stats_container.addWidget(self.card_pressure)
        stats_container.addWidget(self.card_temp)
        stats_container.addWidget(self.card_count)
        main_layout.addLayout(stats_container)

        # main content area
        content_layout = QHBoxLayout()
        
        # chart section
        chart_frame = QFrame()
        chart_frame.setObjectName("Card")
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_header = QHBoxLayout()
        chart_icon = QLabel()
        chart_pix = QPixmap('assets/chart.png')
        if not chart_pix.isNull():
            chart_icon.setPixmap(chart_pix.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        chart_title = QLabel("Equipment Distribution")
        chart_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #334155;")
        
        chart_header.addWidget(chart_icon)
        chart_header.addWidget(chart_title)
        chart_header.addStretch()
        chart_layout.addLayout(chart_header)
        
        self.figure = plt.figure(facecolor='#FFFFFF')
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        # data table section
        table_frame = QFrame()
        table_frame.setObjectName("Card")
        table_layout = QVBoxLayout(table_frame)
        
        # search controls
        search_layout = QHBoxLayout()
        list_icon = QLabel()
        list_pix = QPixmap('assets/list.png')
        if not list_pix.isNull():
             list_icon.setPixmap(list_pix.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
             
        lbl_search = QLabel("Live Data Feed")
        lbl_search.setStyleSheet("font-weight: bold; text-transform: uppercase; font-size: 12px; color: #64748B;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(list_icon)
        search_layout.addWidget(lbl_search)
        search_layout.addStretch()
        search_layout.addWidget(self.search_input)
        table_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flow"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_layout.addWidget(self.table)

        # layout with chart and table
        content_layout.addWidget(chart_frame, stretch=2)
        content_layout.addWidget(table_frame, stretch=3)
        main_layout.addLayout(content_layout)

    def create_stat_card(self, title, value, icon_path):
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QHBoxLayout(frame)
        
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #94A3B8; text-transform: uppercase;")
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        
        self.stats_labels[title] = lbl_value
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        layout.addLayout(text_layout)
        layout.addStretch()
        return frame

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.process_upload(file_path)

    def process_upload(self, path):
        try:
            files = {'file': open(path, 'rb')}
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            response = requests.post(API_URL + "upload/", files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.current_id = data.get('history_id')
                self.update_dashboard(data)
                QMessageBox.information(self, "Success", "File uploaded successfully!")
            elif response.status_code == 401:
                QMessageBox.critical(self, "Auth Error", "Session expired. Please restart.")
            else:
                QMessageBox.critical(self, "Error", f"Upload failed: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error: {e}")

    def download_pdf(self):
        if self.current_id:
            webbrowser.open(f"{API_URL}report/{self.current_id}/")
        else:
            QMessageBox.warning(self, "No Data", "Please upload a CSV file first.")

    def update_dashboard(self, full_data):
        stats = full_data['stats']
        rows = full_data['data']

        # update kpi cards
        self.stats_labels["Avg Pressure"].setText(f"{stats['avg_pressure']} Bar")
        self.stats_labels["Avg Temp"].setText(f"{stats['avg_temp']} °C")
        self.stats_labels["Total Units"].setText(str(stats['total_records']))

        # redraw bar chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        types = list(stats['type_distribution'].keys())
        counts = list(stats['type_distribution'].values())
        colors = ['#0F766E', '#F59E0B', '#3B82F6', '#EF4444']
        ax.bar(types, counts, color=colors[:len(types)])
        ax.set_title("Equipment Distribution", fontsize=12, color='#334155')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.canvas.draw()

        # populate table and highlight critical rows
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            pressure = float(row.get('Pressure', 0))
            temp = float(row.get('Temperature', 0))
            
            # check if reading is critical
            is_critical = pressure > 5.0 or temp > 80

            name_text = f"⚠ {row['Equipment Name']}" if is_critical else row['Equipment Name']
            item_name = QTableWidgetItem(name_text)
            item_type = QTableWidgetItem(row['Type'])
            item_flow = QTableWidgetItem(str(row['Flowrate']))
            item_flow.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # style critical rows
            if is_critical:
                red_bg = QColor(254, 226, 226)
                text_red = QColor(220, 38, 38)
                bold_font = QFont("Segoe UI", weight=QFont.Bold)

                item_name.setBackground(red_bg)
                item_type.setBackground(red_bg)
                item_flow.setBackground(red_bg)
                
                item_name.setForeground(text_red)
                item_name.setFont(bold_font)

            self.table.setItem(i, 0, item_name)
            self.table.setItem(i, 1, item_type)
            self.table.setItem(i, 2, item_flow)

    def filter_table(self, text):
        text = text.lower()
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if text in item.text().lower():
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChemicalVisualizerDesktop()
    window.show()
    sys.exit(app.exec_())