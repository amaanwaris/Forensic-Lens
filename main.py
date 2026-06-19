# =======================================================
# FILENAME: main.py
# DESCRIPTION: Forensic Workstation - High Visibility & Fixed Reporting
# =======================================================
import sys, os, shutil, json, webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QCheckBox,
    QFileDialog, QLabel, QTextEdit, QDialog, QLineEdit, QFormLayout,
    QMessageBox, QHBoxLayout, QFrame, QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog
import threading
from PyQt5.QtGui import QPixmap, QFont, QIntValidator

# --- Core Modules ---
#from modules.timeline import generate_timeline
from modules import metadata_extraction, reporting
from modules.custom_recovery import recover_fat32_images
try: from modules import hash_verification
except: hash_verification = None
try: from modules import tamper_detection
except: tamper_detection = None
try: from modules import social_fingerprint
except: social_fingerprint = None
from modules import ai_detection

# ================= NEON CYBER HIGH-VISIBILITY STYLE =================
STYLE = """
    QMainWindow, QDialog {
        background-color: #050505;
        color: #FFFFFF;
    }
    QFrame#Sidebar {
        background-color: #0D1117;
        border-right: 2px solid #00D1FF;
    }
    QFrame#MainTerminal {
        background-color: #161B22;
        border-radius: 12px;
        margin: 10px;
        border: 1px solid #30363D;
    }
    QLabel {
        color: #00D1FF;
        font-weight: bold;
    }
    QLineEdit, QListWidget {
        background-color: #1A1F26;
        border: 1px solid #00D1FF;
        color: #FFFFFF;
        padding: 10px;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background-color: #00D1FF;
        color: #000000;
        font-weight: bold;
    }
    QPushButton {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        padding: 12px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #2ea043; }
    QPushButton#ActionBtn { 
        background-color: #00D1FF;
        color: #000000;
    }
    QPushButton#ExitBtn {
        background-color: #21262D;
        color: #F85149;
        border: 1px solid #F85149;
    }
    /* Professional Bullet Style for Modules */
    QCheckBox {
        color: #FFFFFF;
        font-size: 13px;
        padding: 8px;
        spacing: 15px;
    }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border-radius: 7px; /* Circular Bullet */
        border: 2px solid #00D1FF;
        background: #000000;
    }
    QCheckBox::indicator:checked {
        background-color: #00D1FF;
        border: 2px solid #FFFFFF;
    }
    QTextEdit {
        background-color: #000000;
        color: #00FF41;
        font-family: 'Consolas', monospace;
        border: 1px solid #30363D;
    }
"""

class CaseSelectionDialog(QDialog):
    def __init__(self, current_base="Cases"):
        super().__init__()
        self.setWindowTitle("Secure Login")
        self.setFixedSize(800, 550)
        self.setStyleSheet(STYLE)
        self.case_dir = None
        self.base_dir = os.path.abspath(current_base)
        os.makedirs(self.base_dir, exist_ok=True)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("📂 INVESTIGATION ARCHIVE"))
        self.case_list = QListWidget()
        self.refresh_cases()
        left.addWidget(self.case_list)
        
        btn_box = QHBoxLayout()
        open_btn = QPushButton("UNLOCK CASE")
        open_btn.setObjectName("ActionBtn")
        open_btn.clicked.connect(self.open_existing)
        btn_box.addWidget(open_btn)
        
        if os.path.basename(self.base_dir) != "Cases":
            up_btn = QPushButton("UP")
            up_btn.clicked.connect(self.go_up)
            btn_box.addWidget(up_btn)
        left.addLayout(btn_box)

        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #0D1117; border-radius: 12px; border: 1px solid #00D1FF;")
        right = QVBoxLayout(right_frame)
        right.addWidget(QLabel("✨ NEW INVESTIGATION"))
        
        self.case_id = QLineEdit(); self.case_id.setPlaceholderText("ID (Numbers Only)")
        self.case_id.setValidator(QIntValidator())
        self.examiner = QLineEdit(); self.examiner.setPlaceholderText("Examiner Name")
        self.password = QLineEdit(); self.password.setPlaceholderText("Key (8+)")
        self.password.setEchoMode(QLineEdit.Password)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.addRow("CASE ID:", self.case_id)
        form.addRow("Examminer:", self.examiner)
        form.addRow("Password:", self.password)
        right.addLayout(form)
        
        create_btn = QPushButton("CREATE ENCRYPTED CASE")
        create_btn.clicked.connect(self.create_new)
        right.addWidget(create_btn)
        right.addStretch()

        main_layout.addLayout(left, 3)
        main_layout.addWidget(right_frame, 2)

    def refresh_cases(self):
        self.case_list.clear()
        if os.path.exists(self.base_dir):
            folders = [f for f in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, f))]
            self.case_list.addItems(sorted(folders, reverse=True))

    def go_up(self):
        self.base_dir = os.path.dirname(self.base_dir); self.refresh_cases()

    def open_existing(self):
        item = self.case_list.currentItem()
        if not item: return
        target = os.path.join(self.base_dir, item.text())
        meta_file = os.path.join(target, ".case_meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                pwd = json.load(f).get("password", "")
            
            check_dlg = QDialog(self)
            check_dlg.setWindowTitle("Auth")
            check_dlg.setStyleSheet(STYLE)
            cl = QVBoxLayout(check_dlg)
            cl.addWidget(QLabel("Enter Case Password:"))
            pi = QLineEdit(); pi.setEchoMode(QLineEdit.Password); cl.addWidget(pi)
            pb = QPushButton("Verify"); cl.addWidget(pb); pb.clicked.connect(check_dlg.accept)
            
            if check_dlg.exec_() == QDialog.Accepted and pi.text() == pwd:
                self.case_dir = target; self.accept()
            else: QMessageBox.critical(self, "Failed", "Access Denied.")
        else:
            self.base_dir = target; self.refresh_cases()

    def create_new(self):
        cid, ex, pwd = self.case_id.text().strip(), self.examiner.text().strip(), self.password.text().strip()
        if not cid.isdigit() or len(pwd) < 8 or not ex:
            QMessageBox.warning(self, "Security", "ID must be Numeric and Password 8+ digits.")
            return
        name = f"CASE_{cid}_{ex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        path = os.path.join(self.base_dir, name)
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "Reports"), exist_ok=True)
        os.makedirs(os.path.join(path, "Inputs"), exist_ok=True)
        with open(os.path.join(path, ".case_meta.json"), 'w') as f:
            json.dump({"id": cid, "examiner": ex, "password": pwd}, f)
        self.case_dir = path; self.accept()

class UDFAApp(QMainWindow):
    def __init__(self, case_dir):
        super().__init__()
        self.device_path = None
        self.case_dir = os.path.abspath(case_dir)
        self.input_path = None
        self.setWindowTitle(f"FORENSIC LENS - {os.path.basename(self.case_dir)}")
        self.resize(1200, 800)
        self.setStyleSheet(STYLE)
        self.init_ui()

    def _recover_data(self):
        device, ok = QInputDialog.getText(
	self,
            "Select Pendrive",
            "Enter device path (example: /dev/sdb1):"
        )

        if not ok or not device:
            self._log("No device entered!", "red")
            return

        self.device_path = device
        self._log(f"[DEVICE] Selected: {device}", "#00D1FF")


    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(320)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel("FORENSIC LENS")
        lbl.setStyleSheet("font-size: 22px; color: #00D1FF; padding-bottom: 10px; border-bottom: 2px solid #00D1FF;")
        side_layout.addWidget(lbl)
        
        self.preview = QLabel("NO PREVIEW")
        self.preview.setFixedSize(280, 220)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("border: 2px dashed #00D1FF; border-radius: 12px; background: #000000; color: #FFFFFF;")
        side_layout.addWidget(self.preview)

        imp_btn = QPushButton("📥 IMPORT EVIDENCE")
        imp_btn.setObjectName("ActionBtn")
        imp_btn.clicked.connect(self._browse)
        side_layout.addWidget(imp_btn)

        # ✅ CUSTOM RECOVERY BUTTON
        rec_btn = QPushButton("🧠 CUSTOM RECOVERY")
        rec_btn.setObjectName("ActionBtn")
        rec_btn.clicked.connect(self._recover_data)
        side_layout.addWidget(rec_btn)

        side_layout.addSpacing(25)
        side_layout.addWidget(QLabel("CHOOSE ANALYZERS"))

        self.modules = {
            "Recovery": QCheckBox("Custom File Recovery"),
            "Meta": QCheckBox("Metadata Extraction"),
            "Hash": QCheckBox("Hash Verification"),
            "Tamper": QCheckBox("Heatmap Scan"),
            "Social": QCheckBox("Social Footprint Trace"),
	    "AI": QCheckBox("AI Generated Detection")
        }

        for cb in self.modules.values():
            side_layout.addWidget(cb)

        side_layout.addStretch()
        run_btn = QPushButton("🚀 START INVESTIGATION"); run_btn.setMinimumHeight(60)
        run_btn.clicked.connect(self._run); side_layout.addWidget(run_btn)
        
        exit_btn = QPushButton("DISCONNECT"); exit_btn.setObjectName("ExitBtn")
        exit_btn.clicked.connect(self.close); side_layout.addWidget(exit_btn)

        # Dashboard
        dash_frame = QFrame(); dash_frame.setObjectName("MainTerminal")
        dash_layout = QVBoxLayout(dash_frame)
        dash_layout.addWidget(QLabel("SYSTEM ANALYSIS LOG"))
        self.log = QTextEdit(); self.log.setReadOnly(True)
        dash_layout.addWidget(self.log)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(dash_frame, 1)

    def _log(self, msg, color="#00FF41"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"<font color='#00D1FF'>[{ts}]</font> <font color='{color}'> > {msg}</font>")

    def _browse(self):
        f, _ = QFileDialog.getOpenFileName(self, "Load Evidence")
        if f:
            dest = os.path.join(self.case_dir, "Inputs", os.path.basename(f))
            shutil.copy2(f, dest); self.input_path = dest
            pix = QPixmap(dest).scaled(270, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview.setPixmap(pix)
            self._log(f"File locked for analysis: {os.path.basename(f)}")

    def _run(self):
	# allow recovery even without file
        if not self.input_path and not self.device_path:
            self._log("No input file or device selected!", "red")
            return
        
        # Reset current directory to case folder before reporting
        os.chdir(self.case_dir)
        
        selected = [n for n, cb in self.modules.items() if cb.isChecked()]
	# RECOVERY MODULE
        if "Recovery" in selected:

            if not self.device_path:
                self._log("[ERROR] No pendrive selected!", "red")
            else:
                num, ok = QInputDialog.getInt(
                    self,
                    "Recovery Limit",
                    "How many files to recover?",
                    6, 1, 50
                )
                if ok:
                    self._log(f"[RECOVERY] Starting for {num} files...")

                    def run_recovery():
                        try:
                            recover_fat32_images(
                                device_path=self.device_path,
                                max_files=num
                               ## log_callback=self._log
                            )
                            self._log("[RECOVERY DONE]", "#00FF41")
                        except Exception as e:
                            self._log(f"[ERROR] {e}", "red")

                    threading.Thread(target=run_recovery).start()
        if not selected:
            self._log("[INFO] No modules selected -> Nothing to run", "yellow")
            return

        self._log("Initiating forensic sequence...")
	# STOP if no file selected
        if not self.input_path:
            self._log("[INFO] No file selected → Skipping analysis & report", "yellow")
            return
        meta, hashes, tamper, social = {}, {}, {}, {}
	#  DEVICE CHECK
        if not hasattr(self, 'device_path') or not self.device_path:
            self._log("[ERROR] No pendrive selected!", "red")
        else:
        #  ASK FILE COUNT
            num, ok = QInputDialog.getInt(
                self,
                "Recovery Limit",
                "How many files to recover?",
                6, 1, 50
            )

            if ok:
                self._log(f"[INFO] Recovering {num} files...")

        
        if "Meta" in selected or "Social" in selected:
            meta = metadata_extraction.extract_metadata(self.input_path) or {}
            self._log("Metadata extracted.")
        if "Hash" in selected and hash_verification:
            hashes = hash_verification.calculate_hashes(self.input_path) or {}
            self._log("Hashes generated.")
        if "Tamper" in selected and tamper_detection:
            tamper = tamper_detection.quick_tamper_check(self.input_path) or {}
            self._log("Heatmap analysis complete.")
        if "Social" in selected and social_fingerprint:
            social = social_fingerprint.analyze_social_fingerprint(self.input_path, meta) or {}
            self._log("Social discovery complete.")
        if "AI" in selected:
            ai_result = ai_detection.detect_ai_image(self.input_path)
            self._log(f"AI Detection → {ai_result}")

        try:
            # Absolute report path ensure
            report_path = reporting.generate_report(self.input_path, selected, meta, hashes, tamper, social)
            self._log("SUCCESS: Investigation report compiled.")
            if report_path and os.path.exists(report_path):
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
                self._log(f"Opening report: {os.path.basename(report_path)}")
        except Exception as e:
            self._log(f"Reporting Error: {e}", "red")

if __name__ == "__main__":
    app = QApplication(sys.argv); mgr = CaseSelectionDialog()
    if mgr.exec_() == QDialog.Accepted:
        win = UDFAApp(mgr.case_dir); win.show(); sys.exit(app.exec_())
