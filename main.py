import sys
import time
import math
import winsound
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QSystemTrayIcon, QMenu, QAction, QDialog, 
                             QFormLayout, QSpinBox, QComboBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer, QPoint , QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QPainterPath, QPixmap, QIcon, QRadialGradient, QLinearGradient , QFont
from pynput import keyboard

# ==========================================
# 1. THE SETTINGS DASHBOARD
# ==========================================
class DashboardWindow(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.setWindowTitle("Cat Companion Setup")
        self.setFixedSize(320, 380)
        
        layout = QVBoxLayout()
        header = QLabel("🐱 Configure Companion")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        form = QFormLayout()
        
        self.monitor_dropdown = QComboBox()
        for i in range(QApplication.desktop().screenCount()):
            self.monitor_dropdown.addItem(f"Display {i + 1}")
        form.addRow("Target Monitor:", self.monitor_dropdown)
        
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Midnight Dark", "Ginger Tabby", "Snow White"])
        form.addRow("Cat Theme:", self.theme_dropdown)

        self.fps_dropdown = QComboBox()
        self.fps_dropdown.addItems(["60 FPS (Standard)", "30 FPS (Battery Saver)", "144 FPS (Ultra Smooth)"])
        form.addRow("Animation Speed:", self.fps_dropdown)
        
        self.work_spinner = QSpinBox()
        self.work_spinner.setRange(1, 120)
        self.work_spinner.setValue(25)
        form.addRow("Focus Time (min):", self.work_spinner)
        
        self.break_spinner = QSpinBox()
        self.break_spinner.setRange(1, 30)
        self.break_spinner.setValue(5)
        form.addRow("Break Time (min):", self.break_spinner)
        
        layout.addLayout(form)
        
        self.launch_btn = QPushButton("🚀 Launch / Update")
        self.launch_btn.setStyleSheet("padding: 15px; font-weight: bold; background-color: #2ea043; color: white; border-radius: 5px; margin-top: 20px;")
        self.launch_btn.clicked.connect(self.launch_app)
        layout.addWidget(self.launch_btn)
        self.setLayout(layout)

    def launch_app(self):
        target_screen = self.monitor_dropdown.currentIndex()
        theme_index = self.theme_dropdown.currentIndex()
        work_time = self.work_spinner.value() * 60
        
        fps_choice = self.fps_dropdown.currentIndex()
        if fps_choice == 0: ms_per_frame = 16 
        elif fps_choice == 1: ms_per_frame = 33 
        else: ms_per_frame = 7  

        self.app_controller.start_or_update_companion(target_screen, work_time, theme_index, ms_per_frame)
        self.hide()

# ==========================================
# 2. THE PERFECT PROCEDURAL CAT
# ==========================================
class ProceduralCat(QWidget):
    def __init__(self, target_screen, theme_index, ms_per_frame, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.theme = theme_index
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300) 
        
        self.move_to_screen(target_screen)
        
        self.dragging = False
        self.offset = QPoint()
        self.paw_l_down = False
        self.paw_r_down = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(ms_per_frame) 

    def move_to_screen(self, target_screen):
        screen_geo = QApplication.desktop().screenGeometry(target_screen)
        self.move(screen_geo.x() + (screen_geo.width() // 2) - 150,
                  screen_geo.y() + screen_geo.height() - 320)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos() 

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #2d333b; color: white; border: 1px solid #444c56; border-radius: 5px; padding: 5px;}
            QMenu::item { padding: 8px 20px; }
            QMenu::item:selected { background-color: #2ea043; border-radius: 3px; }
        """)
        
        # --- NEW POMODORO MENU SECTION ---
        if self.app_controller.is_timer_running:
            mins = self.app_controller.time_left // 60
            secs = self.app_controller.time_left % 60
            pomo_action = menu.addAction(f"🛑 Stop Focus ({mins}:{secs:02d})")
        else:
            pomo_action = menu.addAction("🍅 Start Focus Time")
            
        menu.addSeparator()
        settings_action = menu.addAction("⚙️ Settings Dashboard")
        quit_action = menu.addAction("❌ Exit Companion")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == pomo_action:
            if self.app_controller.is_timer_running:
                self.app_controller.stop_pomodoro()
            else:
                self.app_controller.start_pomodoro()
        elif action == settings_action:
            self.app_controller.dashboard.show()
            self.app_controller.dashboard.activateWindow()
        elif action == quit_action:
            self.app_controller.quit_app()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.theme == 0:   # Midnight Dark
            fur_light = QColor(65, 72, 85)
            fur_dark = QColor(15, 18, 22)      
            outline_color = QColor(255, 255, 255)
            inner_ear = QColor(45, 25, 30)
        elif self.theme == 1: # Ginger Tabby
            fur_light = QColor(245, 175, 95)
            fur_dark = QColor(170, 85, 30) 
            outline_color = QColor(255, 255, 255)
            inner_ear = QColor(220, 130, 130)
        else:                 # Snow White
            fur_light = QColor(255, 255, 255)
            fur_dark = QColor(220, 225, 230)
            outline_color = QColor(0, 0, 0) 
            inner_ear = QColor(30, 30, 30)  

        blush_color = QColor(255, 120, 120, 80)
        
        head_grad = QRadialGradient(150, 100, 90)
        head_grad.setColorAt(0, fur_light)
        head_grad.setColorAt(1, fur_dark)
        
        body_grad = QRadialGradient(150, 160, 80)
        body_grad.setColorAt(0, fur_light)
        body_grad.setColorAt(1, fur_dark)

        main_pen = QPen(outline_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        global_mouse = QCursor.pos()
        eye_center = self.mapToGlobal(QPoint(150, 110))
        angle = math.atan2(global_mouse.y() - eye_center.y(), global_mouse.x() - eye_center.x())

        # 1. TAIL
        tail_path = QPainterPath()
        tail_path.moveTo(200, 170)
        tail_path.cubicTo(260, 190, 280, 130, 240, 90) 
        
        painter.setPen(QPen(outline_color, 16, Qt.SolidLine, Qt.RoundCap))
        painter.drawPath(tail_path)
        tail_grad = QLinearGradient(200, 170, 240, 90)
        tail_grad.setColorAt(0, fur_dark)
        tail_grad.setColorAt(1, fur_light)
        painter.setPen(QPen(QBrush(tail_grad), 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawPath(tail_path)

        # 2. EARS
        painter.setBrush(QBrush(head_grad))
        painter.setPen(main_pen)
        
        ear_l = QPainterPath()
        ear_l.moveTo(95, 90)
        ear_l.quadTo(60, 50, 75, 25)
        ear_l.quadTo(110, 35, 125, 70) 
        painter.drawPath(ear_l)
        
        ear_r = QPainterPath()
        ear_r.moveTo(205, 90)
        ear_r.quadTo(240, 50, 225, 25)
        ear_r.quadTo(190, 35, 175, 70)
        painter.drawPath(ear_r)
        
        painter.setBrush(QBrush(inner_ear))
        painter.setPen(Qt.NoPen)
        in_ear_l = QPainterPath()
        in_ear_l.moveTo(93, 85)
        in_ear_l.quadTo(70, 55, 78, 40)
        in_ear_l.quadTo(100, 45, 115, 75)
        painter.drawPath(in_ear_l)
        
        in_ear_r = QPainterPath()
        in_ear_r.moveTo(207, 85)
        in_ear_r.quadTo(230, 55, 222, 40)
        in_ear_r.quadTo(200, 45, 185, 75)
        painter.drawPath(in_ear_r)

        # 3. BODY
        chest = QPainterPath()
        chest.addEllipse(100, 110, 100, 80) 
        hips = QPainterPath()
        hips.addEllipse(85, 140, 130, 60)  
        body_path = chest.united(hips)
        
        painter.setBrush(QBrush(body_grad))
        painter.setPen(main_pen)
        painter.drawPath(body_path)

        # 4. FACE
        forehead = QPainterPath()
        forehead.addEllipse(75, 55, 150, 90) 
        cheek_l = QPainterPath()
        cheek_l.addEllipse(60, 85, 60, 65)  
        cheek_r = QPainterPath()
        cheek_r.addEllipse(180, 85, 60, 65) 
        head_path = forehead.united(cheek_l).united(cheek_r)
        
        painter.setBrush(QBrush(head_grad))
        painter.setPen(main_pen)
        painter.drawPath(head_path)

        # 5. FACE DETAILS
        painter.setBrush(QBrush(QColor(255, 255, 255))) 
        painter.setPen(main_pen)
        painter.drawEllipse(105, 100, 32, 32)
        painter.drawEllipse(163, 100, 32, 32)
        
        painter.setBrush(QBrush(QColor(20, 20, 20))) 
        painter.setPen(Qt.NoPen)
        p_offset_x = math.cos(angle) * 7
        p_offset_y = math.sin(angle) * 7
        painter.drawEllipse(int(112 + p_offset_x), int(108 + p_offset_y), 16, 16)
        painter.drawEllipse(int(170 + p_offset_x), int(108 + p_offset_y), 16, 16)

        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(80, 125, 30, 15)
        painter.drawEllipse(190, 125, 30, 15)

        painter.setBrush(QBrush(outline_color))
        painter.drawEllipse(146, 125, 8, 5)
        
        painter.setPen(main_pen)
        painter.setBrush(Qt.NoBrush)
        mouth = QPainterPath()
        mouth.moveTo(140, 132)
        mouth.arcTo(140, 132, 10, 10, 180, 180)
        mouth.arcTo(150, 132, 10, 10, 180, 180)
        painter.drawPath(mouth)

        painter.drawArc(40, 115, 40, 20, 30 * 16, 120 * 16)
        painter.drawArc(35, 125, 40, 20, 20 * 16, 120 * 16)
        painter.drawArc(220, 115, 40, 20, 30 * 16, 120 * 16)
        painter.drawArc(225, 125, 40, 20, 40 * 16, 120 * 16)

        # 6. KEYBOARD
        painter.setBrush(QBrush(QColor(80, 85, 95)))
        painter.setPen(QPen(outline_color, 2))
        painter.drawRoundedRect(55, 200, 190, 35, 8, 8)
        
        painter.setBrush(QBrush(QColor(180, 185, 190)))
        painter.setPen(Qt.NoPen)
        start_x = 65
        for i in range(10):
            painter.drawRoundedRect(start_x + (i * 17), 205, 13, 10, 3, 3)
        for i in range(9):
            painter.drawRoundedRect(start_x + 8 + (i * 17), 218, 13, 10, 3, 3)

        # --- POMODORO TIMER (Cute & Adorable) ---
        
        if self.app_controller.is_timer_running:
            painter.setPen(QPen(outline_color, 2))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            mins = self.app_controller.time_left // 60
            secs = self.app_controller.time_left % 60
            painter.drawText(QRect(55, 242, 190, 20), Qt.AlignCenter, f"{mins:02d}:{secs:02d}")

        # 7. PAWS
        painter.setBrush(QBrush(body_grad))
        painter.setPen(main_pen)
        
        left_y = 205 if self.paw_l_down else 185
        painter.drawEllipse(80, left_y - 20, 35, 28)
        
        right_y = 205 if self.paw_r_down else 185
        painter.drawEllipse(185, right_y - 20, 35, 28)

# ==========================================
# 3. APP CONTROLLER
# ==========================================
class AppController:
    def __init__(self):
        self.dashboard = DashboardWindow(self)
        self.dashboard.show()
        
        self.cat = None
        self.tray_icon = None
        self.listener = None
        
        self.pomodoro_work_time = 0
        self.time_left = 0
        self.is_timer_running = False
        
        self.pomo_timer = QTimer()
        self.pomo_timer.timeout.connect(self.pomodoro_tick)

    def start_or_update_companion(self, target_screen, work_time, theme_index, ms_per_frame):
        self.pomodoro_work_time = work_time
        
        if not self.cat:
            self.cat = ProceduralCat(target_screen, theme_index, ms_per_frame, self)
            self.cat.show()
            
            self.last_press_time = 0
            self.current_paw = True
            self.listener = keyboard.Listener(on_press=self.on_key_press)
            self.listener.start()
            
            self.logic_timer = QTimer()
            self.logic_timer.timeout.connect(self.update_logic)
            self.logic_timer.start(50)
            
            self.setup_tray()
        else:
            self.cat.theme = theme_index
            self.cat.timer.setInterval(ms_per_frame) 
            self.cat.move_to_screen(target_screen)
            self.cat.update() 

    def setup_tray(self):
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.transparent)
        p = QPainter(icon_pixmap)
        p.setBrush(QColor(15, 18, 22))
        p.drawEllipse(2, 2, 28, 28)
        p.end()
        
        self.tray_icon = QSystemTrayIcon(QIcon(icon_pixmap), QApplication.instance())
        menu = QMenu()
        pomo_action = QAction("Open Settings", menu)
        pomo_action.triggered.connect(self.dashboard.show)
        menu.addAction(pomo_action)
        menu.addSeparator()
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def start_pomodoro(self):
        self.is_timer_running = True
        self.time_left = self.pomodoro_work_time
        self.pomo_timer.start(1000)
        if self.cat: self.cat.update()

    def stop_pomodoro(self):
        self.is_timer_running = False
        self.pomo_timer.stop()
        self.time_left = self.pomodoro_work_time
        if self.cat: self.cat.update()

    def pomodoro_tick(self):
        if self.is_timer_running:
            self.time_left -= 1
            if self.cat: self.cat.update() # Refreshes the cat's screen every second!
            
            if self.time_left <= 0:
                self.is_timer_running = False
                self.pomo_timer.stop()
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.tray_icon.showMessage("Time's Up!", "Take a break.", QSystemTrayIcon.Information, 5000)
                self.time_left = self.pomodoro_work_time # Reset for next session
                if self.cat: self.cat.update()

    def on_key_press(self, key):
        if not self.cat: return
        self.last_press_time = time.time()
        if self.current_paw:
            self.cat.paw_l_down = True
            self.cat.paw_r_down = False
        else:
            self.cat.paw_l_down = False
            self.cat.paw_r_down = True
        self.current_paw = not self.current_paw

    def update_logic(self):
        if not self.cat: return
        if time.time() - self.last_press_time > 0.15:
            self.cat.paw_l_down = False
            self.cat.paw_r_down = False

    def quit_app(self):
        if self.listener: self.listener.stop()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    controller = AppController()
    sys.exit(app.exec_())