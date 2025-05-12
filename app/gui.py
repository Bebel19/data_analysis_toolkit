# app/gui.py
import os
from utils.logger import logger

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QStackedLayout, QFileDialog, QFormLayout,
    QLineEdit, QHBoxLayout, QMessageBox
)

from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtCore import Qt

from app.controller import ScriptController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toolkit de Traitement CSV")
        self.setMinimumSize(600, 400)

        self.controller = ScriptController()

        self.container = QWidget()
        self.layout = QStackedLayout()
        self.container.setLayout(self.layout)

        self.init_script_selection_screen()
        self.init_parameters_screen()

        self.setCentralWidget(self.container)

    def init_script_selection_screen(self):
        self.script_list_screen = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Choisir un script de traitement :")
        self.script_list_widget = QListWidget()
        for script_name in self.controller.get_script_names():
            self.script_list_widget.addItem(script_name)

        select_button = QPushButton("Suivant")
        select_button.clicked.connect(self.load_selected_script)

        layout.addWidget(label)
        layout.addWidget(self.script_list_widget)
        layout.addWidget(select_button)

        self.script_list_screen.setLayout(layout)
        self.layout.addWidget(self.script_list_screen)

    def init_parameters_screen(self):
        self.parameters_screen = QWidget()
        self.parameters_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.input_fields = {}
        self.selected_script = None

        self.input_file_btn = QPushButton("Sélectionner un fichier CSV (si requis)")
        self.input_file_btn.clicked.connect(self.select_input_file)
        self.input_file_path = ""

        self.output_file_btn = QPushButton("Choisir le fichier de sortie")
        self.output_file_btn.clicked.connect(self.select_output_file)
        self.output_file_path = ""

        self.run_button = QPushButton("Lancer le traitement")  # ← définie ici AVANT l’ajout
        self.run_button.clicked.connect(self.run_script)

        self.parameters_layout.addLayout(self.form_layout)
        self.parameters_screen.setLayout(self.parameters_layout)
        self.layout.addWidget(self.parameters_screen)

    def load_selected_script(self):
        selected_items = self.script_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Aucun script sélectionné.")
            return

        script_name = selected_items[0].text()
        self.selected_script = self.controller.load_script(script_name)

        self.clear_layout(self.parameters_layout)
        self.form_layout = QFormLayout()
        self.parameters_layout.addLayout(self.form_layout)
        self.input_fields.clear()

        for param, meta in self.selected_script["parameters"].items():
            param_type = meta.get("type", "string")
            default = meta.get("default", "")

            if param_type == "int":
                from PyQt5.QtWidgets import QSpinBox
                widget = QSpinBox()
                widget.setMaximum(1_000_000)
                widget.setValue(int(default))
            elif param_type == "float":
                from PyQt5.QtWidgets import QDoubleSpinBox
                widget = QDoubleSpinBox()
                widget.setDecimals(4)
                widget.setMaximum(1_000_000)
                widget.setValue(float(default))
            elif param_type == "bool":
                from PyQt5.QtWidgets import QCheckBox
                widget = QCheckBox()
                widget.setChecked(bool(default))
            else:
                widget = QLineEdit()
                widget.setText(str(default))

            self.input_fields[param] = widget
            self.form_layout.addRow(f"{param} :", widget)

        # Toujours injecter les bons widgets
        if self.selected_script.get("input_required", False):
            self.parameters_layout.addWidget(self.input_file_btn)

        self.parameters_layout.addWidget(self.output_file_btn)
        self.parameters_layout.addWidget(self.run_button)

        self.layout.setCurrentWidget(self.parameters_screen)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier CSV", "", "Fichiers CSV (*.csv)")
        if file_path:
            self.input_file_path = file_path

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choisir le fichier de sortie",
            "",
            "Fichiers CSV (*.csv)"
        )
        if file_path:
            self.output_file_path = file_path
            self.output_file_btn.setText(f"Sortie : {file_path}")

    def run_script(self):
        logger.info(f"Début traitement utilisateur : {self.selected_script['name']}")

        if not self.output_file_path:
            QMessageBox.warning(self, "Erreur", "Veuillez choisir un fichier de sortie.")
            return  # ← manquant

        output_dir = os.path.dirname(self.output_file_path)
        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Erreur", f"Dossier de sortie inexistant : {output_dir}")
            return

        if not os.access(output_dir, os.W_OK):
            QMessageBox.critical(self, "Erreur", f"Dossier non accessible en écriture : {output_dir}")
            return

        params = {}
        for key, widget in self.input_fields.items():
            param_type = self.selected_script["parameters"][key].get("type", "string")
            if param_type == "int":
                params[key] = widget.value()
            elif param_type == "float":
                params[key] = widget.value()
            elif param_type == "bool":
                params[key] = widget.isChecked()
            else:
                params[key] = widget.text() or self.selected_script["parameters"][key].get("default", "")

        try:
            self.controller.execute_script(
                self.selected_script["name"],
                input_file=self.input_file_path,
                output_file=self.output_file_path,
                params=params
            )
            QMessageBox.information(self, "Succès", "Traitement terminé.")
            self.layout.setCurrentWidget(self.script_list_screen)
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exécution", str(e))

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.deleteLater()

class WorkerThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, controller, script_name, input_file, output_file, params):
        super().__init__()
        self.controller = controller
        self.script_name = script_name
        self.input_file = input_file
        self.output_file = output_file
        self.params = params

    def run(self):
        try:
            self.controller.execute_script(
                self.script_name,
                input_file=self.input_file,
                output_file=self.output_file,
                params=self.params
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
