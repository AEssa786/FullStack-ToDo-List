from PySide6.QtWidgets import *
from PySide6.QtCore import QDate
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QColor
import logic
import sys
import os

class Display(QMainWindow):
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def __init__(self):
        super().__init__()
        
        self.selected_card = None
        
        logo_path = self.resource_path("ToDo/notepad.png")
        
        self.setWindowTitle("ToDo List")
        self.setWindowIcon(QIcon(logo_path))
        self.setMinimumSize(1000, 600)

        # Main container
        container = QWidget()
        self.setCentralWidget(container)

        # Main layout
        main_layout = QHBoxLayout(container)

        # Sidebar layout
        sidebar = QVBoxLayout()
        sidebar.setSpacing(15)

        # Buttons with emojis
        self.viewButton = QPushButton("📋  View Tasks")
        self.viewButton.clicked.connect(self.showCategory)

        self.addButton = QPushButton("➕  Add Task")
        self.addButton.clicked.connect(self.addTask)

        self.deleteButton = QPushButton("🗑️  Delete Task")
        self.deleteButton.clicked.connect(self.deleteTask)

        self.editButton = QPushButton("✏️  Edit Task")
        self.editButton.clicked.connect(self.editTask)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        for btn in [self.viewButton, self.addButton, self.editButton, self.deleteButton]:
            btn.setFixedWidth(140)
            button_layout.addWidget(btn)

        button_container = QWidget()
        button_container.setLayout(button_layout)

        sidebar.addStretch()  # push to middle
        sidebar.addWidget(button_container)
        sidebar.addStretch()

        
        main_layout.addLayout(sidebar)

        # Right side: title + scroll area
        right_layout = QVBoxLayout()

        title = QLabel("📌 To Do List")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 15px 0;")
        right_layout.addWidget(title)

        self.taskScrollArea = QScrollArea()
        self.taskScrollArea.setWidgetResizable(True)

        self.taskContent = QWidget()
        self.taskLayout = QVBoxLayout(self.taskContent)
        self.taskLayout.setAlignment(Qt.AlignTop)
        self.taskScrollArea.setWidget(self.taskContent)

        right_layout.addWidget(self.taskScrollArea)
        main_layout.addLayout(right_layout)

    # --- Create a card widget for each task ---
    def create_task_card(self, title, module=None, due_date=None, description="", status="pending", task_id=None, task_type=None):
        card = QFrame()
        card.setObjectName("taskCard")
        card.setProperty("selected", False)

        # Attach metadata
        card.task_id = task_id
        card.task_type = task_type
        card.task_data = {
            "title": title,
            "module": module,
            "due_date": due_date,
            "description": description
        }

        layout = QVBoxLayout(card)

        titleLabel = QLabel(f"<b>{title}</b>")
        titleLabel.setStyleSheet("font-size: 16px;")

        # Dynamic info row based on task_type
        infoText = ""
        if task_type == "campus":
            infoText = f"Module: <b>{module}</b> | Due: {due_date}"
        elif task_type == "project":
            infoText = f"Tech Stack: <b>{module}</b> | Level: {due_date}"
        elif task_type == "learning":
            infoText = f"Language: <b>{module}</b>"
        elif task_type == "general":
            infoText = ""

        infoLabel = QLabel(infoText)
        descLabel = QLabel(f"Description: {description}")

        statusIcon = QLabel("🕒" if status == "pending" else "✅" if status == "done" else "⚠️")
        statusIcon.setAlignment(Qt.AlignRight)

        topRow = QHBoxLayout()
        topRow.addWidget(titleLabel)
        topRow.addWidget(statusIcon)

        layout.addLayout(topRow)
        if infoText:
            layout.addWidget(infoLabel)
        layout.addWidget(descLabel)

        # Selection behavior
        card.mousePressEvent = lambda event: self.select_card(card)

        return card


    def select_card(self, card):
        print("Card selected:", card.task_id)

        if self.selected_card and self.selected_card != card:
            self.selected_card.setProperty("selected", False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)

        card.setProperty("selected", True)
        card.style().unpolish(card)
        card.style().polish(card)
        self.selected_card = card

    
    # --- Clear previous cards ---
    def clear_tasks(self):
        for i in reversed(range(self.taskLayout.count())):
            widget = self.taskLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    # --- Add methods ---
    def addTask(self):
        taskDialog = addCategory()
        taskDialog.exec()

    def showCategory(self):
        categoryDialog = showCategory(self)
        categoryDialog.exec()
        
    def deleteTask(self):
        if not self.selected_card:
            QMessageBox.warning(self, "Warning", "Please select a task to delete.")
            return

        task_id = self.selected_card.task_id
        task_type = self.selected_card.task_type

        if task_type == "campus":
            logic.cursor.execute("DELETE FROM campus WHERE assignmentID = %s", (task_id,))
        elif task_type == "project":
            logic.cursor.execute("DELETE FROM projects WHERE projectID = %s", (task_id,))
        elif task_type == "learning":
            logic.cursor.execute("DELETE FROM learn WHERE techID = %s", (task_id,))
        elif task_type == "general":
            logic.cursor.execute("DELETE FROM generalTask WHERE taskID = %s", (task_id,))
        else:
            QMessageBox.warning(self, "Error", "Unknown task type.")
            return

        logic.db.commit()
        self.clear_tasks()
        self.selected_card = None
        QMessageBox.information(self, "Deleted", "Task deleted successfully.")

        
    def editTask(self):
        if not self.selected_card:
            QMessageBox.warning(self, "Warning", "Please select a task to edit.")
            return

        task_type = self.selected_card.task_type
        task_id = self.selected_card.task_id
        data = self.selected_card.task_data

        print(f"Editing {task_type} task with ID: {task_id}")

        if task_type == "campus":
            dialog = AddCampusTaskDialog()
            dialog.taskID = task_id
            dialog.save.setEnabled(False)
            dialog.taskName.setText(data["title"])
            dialog.moduleName.setCurrentText(data["module"])
            dialog.dueDate.setDate(QDate.fromString(data["due_date"], "yyyy-MM.dd"))
            dialog.taskDescription.setText(data["description"])
            dialog.exec()

        elif task_type == "project":
            dialog = AddProjectTaskDialog()
            dialog.taskID = task_id
            dialog.save.setEnabled(False)
            dialog.taskName.setText(data["title"])
            dialog.techStack.setText(data["module"])
            dialog.descr.setText(data["description"])
            dialog.level.setCurrentText(data["due_date"])  # Placeholder (can't derive from card)
            dialog.exec()

        elif task_type == "learning":
            dialog = addLearningTaskDialog()
            dialog.taskID = task_id
            dialog.save.setEnabled(False)
            dialog.taskName.setText(data["title"])
            dialog.lang.setText(data["module"])
            dialog.descr.setText(data["description"])
            dialog.exec()

        elif task_type == "general":
            dialog = AddGeneralTaskDialog()
            dialog.taskID = task_id
            dialog.save.setEnabled(False)
            dialog.taskName.setText(data["title"])
            dialog.descr.setText(data["description"])
            dialog.exec()

        self.selected_card = None
        self.clear_tasks()


 
         
         
#--------------------------------------View Tasks--------------------------------------#   
    
class showCategory(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Show Tasks")
        self.setMinimumSize(300, 200)
        self.parent = parent
        
        self.all = QPushButton("All Tasks", self)
        self.all.clicked.connect(self.showAllTasks)
        
        self.Campus = QPushButton("Campus", self)
        self.Campus.clicked.connect(self.showCampusTask)
        
        self.project = QPushButton("Project", self)
        self.project.clicked.connect(self.showProjectTask)
        
        self.learning = QPushButton("Learning", self)
        self.learning.clicked.connect(self.showLearningTask)
        
        self.general = QPushButton("General", self)
        self.general.clicked.connect(self.showGeneralTask)

        
        layout = QVBoxLayout()
        layout.addWidget(self.all)
        layout.addWidget(self.Campus)
        layout.addWidget(self.project)
        layout.addWidget(self.learning)
        layout.addWidget(self.general)
        self.setLayout(layout)
        
    def showCampusTask(self):
        self.parent.clear_tasks()
        for task in logic.campus_tasks():
            card = self.parent.create_task_card(task[1], task[2], task[3], task[4], task_id=task[0], task_type="campus")
            self.parent.taskLayout.addWidget(card)
        self.close()

    def showProjectTask(self):
        self.parent.clear_tasks()
        for task in logic.project_tasks():
            card = self.parent.create_task_card(task[1], task[2], task[4], description=task[3], task_id=task[0], task_type="project")
            self.parent.taskLayout.addWidget(card)
        self.close()

    def showLearningTask(self):
        self.parent.clear_tasks()
        for task in logic.learning_tasks():
            card = self.parent.create_task_card(task[1], task[2], description=task[3], task_id=task[0], task_type="learning")
            self.parent.taskLayout.addWidget(card)
        self.close()

    def showGeneralTask(self):
        self.parent.clear_tasks()
        for task in logic.general_tasks():
            card = self.parent.create_task_card(task[1], description=task[2], task_id=task[0], task_type="general")
            self.parent.taskLayout.addWidget(card)
        self.close()

    def showAllTasks(self):
        self.parent.clear_tasks()
        for task in logic.campus_tasks():
            card = self.parent.create_task_card(task[1], task[2], task[3], task[4], task_id=task[0], task_type="campus")
            self.parent.taskLayout.addWidget(card)
        for task in logic.project_tasks():
            card = self.parent.create_task_card(task[1], task[2], task[4], description=task[3], task_id=task[0], task_type="project")
            self.parent.taskLayout.addWidget(card)
        for task in logic.learning_tasks():
            card = self.parent.create_task_card(task[1], task[2], description=task[3], task_id=task[0], task_type="learning")
            self.parent.taskLayout.addWidget(card)
        for task in logic.general_tasks():
            card = self.parent.create_task_card(task[1], description=task[2], task_id=task[0], task_type="general")
            self.parent.taskLayout.addWidget(card)
        self.close()
        
            
        
    
#--------------------------------------Add Tasks--------------------------------------#  
    
class addCategory(QDialog):
    def __init__(self):
        self.taskID = None

        super().__init__()
        self.setWindowTitle("Add Tasks")
        self.setMinimumSize(300, 200)
        
        self.Campus = QPushButton("Campus", self)
        self.Campus.clicked.connect(self.addCampusTask)
        
        self.project = QPushButton("Project", self)
        self.project.clicked.connect(self.addProjectTask)
        
        self.learning = QPushButton("Learning", self)
        self.learning.clicked.connect(self.addLearningTask)
        
        self.general = QPushButton("General", self)
        self.general.clicked.connect(self.addGeneralTask)

        
        layout = QVBoxLayout()
        layout.addWidget(self.Campus)
        layout.addWidget(self.project)
        layout.addWidget(self.learning)
        layout.addWidget(self.general)
        self.setLayout(layout)
        
    def addCampusTask(self):
        taskDialog = AddCampusTaskDialog()
        taskDialog.update.setEnabled(False)
        taskDialog.exec()
        self.close()
        
    def addProjectTask(self):
        taskDialog = AddProjectTaskDialog()
        taskDialog.update.setEnabled(False)
        taskDialog.exec()
        self.close()
        
    def addLearningTask(self):
        taskDialog = addLearningTaskDialog()
        taskDialog.update.setEnabled(False)
        taskDialog.exec()
        self.close()
        
    def addGeneralTask(self):
        taskDialog = AddGeneralTaskDialog()
        taskDialog.update.setEnabled(False)
        taskDialog.exec()
        self.close()
    
    
class AddCampusTaskDialog(QDialog):
    def __init__(self):
        self.taskID = None

        super().__init__()
        self.setWindowTitle("Add Campus Task")
        self.setMinimumSize(300, 200)
        
        self.taskName = QLineEdit(self)
        self.moduleName = QComboBox(self)
        self.dueDate = QDateEdit(self)
        self.dueDate.setDisplayFormat("dd/MM/yyyy")
        self.dueDate.setCalendarPopup(True)
        self.dueDate.setDate(QDate.currentDate())
        self.taskDescription = QLineEdit(self)
        
        logic.cursor.execute("SELECT module FROM modules")
        for module in logic.cursor.fetchall():
            self.moduleName.addItem(module[0])
        
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.saveTask)
        
        self.update = QPushButton("Update", self)
        self.update.clicked.connect(self.updateTask)
        
        self.cancel = QPushButton("Cancel", self)
        self.cancel.clicked.connect(self.close)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.save)
        buttonLayout.addWidget(self.update)
        buttonLayout.addWidget(self.cancel)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Task Name:"))
        layout.addWidget(self.taskName)
        layout.addWidget(QLabel("Module Name:"))
        layout.addWidget(self.moduleName)
        layout.addWidget(QLabel("Due Date:"))
        layout.addWidget(self.dueDate)
        layout.addWidget(QLabel("Task Description:"))
        layout.addWidget(self.taskDescription)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def saveTask(self):
        name = self.taskName.text()
        module = self.moduleName.currentText()
        dueDate = self.dueDate.date().toString("yyyy-MM.dd")
        task = self.taskDescription.text()
        
        logic.add_campus_task(name, module, dueDate, task)
        
        self.close()
        
    def updateTask(self):
        name = self.taskName.text()
        module = self.moduleName.currentText()
        dueDate = self.dueDate.date().toString("yyyy-MM.dd")
        task = self.taskDescription.text()
        
        logic.cursor.execute("UPDATE campus SET name = %s, module = %s, dueDate = %s, descr = %s WHERE assignmentID = %s",
                              (name, module, dueDate, task, self.taskID))
        logic.db.commit()
        
        self.close()
        
        
class AddProjectTaskDialog(QDialog):
    def __init__(self):
        self.taskID = None

        super().__init__()
        self.setWindowTitle("Add Project Task")
        self.setMinimumSize(300, 200)
        
        self.taskName = QLineEdit(self)
        self.techStack = QLineEdit(self)
        self.descr = QLineEdit(self)
        self.level = QComboBox(self)
        self.level.addItems(["Easy", "Intermediate", "Difficult"])
        
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.saveTask)
        
        self.update = QPushButton("Update", self)
        self.update.clicked.connect(self.updateTask)
        
        self.cancel = QPushButton("Cancel", self)
        self.cancel.clicked.connect(self.close)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.save)
        buttonLayout.addWidget(self.update)
        buttonLayout.addWidget(self.cancel)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Project Name:"))
        layout.addWidget(self.taskName)
        layout.addWidget(QLabel("Tech Stack:"))
        layout.addWidget(self.techStack)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.descr)
        layout.addWidget(QLabel("Difficulty Level:"))
        layout.addWidget(self.level)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def saveTask(self):
        name = self.taskName.text()
        techStack = self.techStack.text()
        descr = self.descr.text()
        level = self.level.currentText()
        
        logic.add_project_task(name, techStack, descr, level)
        
        self.close()
        
    def updateTask(self):
        name = self.taskName.text()
        techStack = self.techStack.text()
        descr = self.descr.text()
        level = self.level.currentText()
        
        logic.cursor.execute("UPDATE projects SET name = %s, techStack = %s, descr = %s, level = %s WHERE projectID = %s",
                              (name, techStack, descr, level, self.taskID))
        logic.db.commit()
        
        self.close()
        
        
class addLearningTaskDialog(QDialog):
    def __init__(self):
        self.taskID = None

        super().__init__()
        self.setWindowTitle("Add Learning Task")
        self.setMinimumSize(300, 200)
        
        self.taskName = QLineEdit(self)
        self.lang = QLineEdit(self)
        self.descr = QLineEdit(self)
        
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.saveTask)
        
        self.update = QPushButton("Update", self)
        self.update.clicked.connect(self.updateTask)
        
        self.cancel = QPushButton("Cancel", self)
        self.cancel.clicked.connect(self.close)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.save)
        buttonLayout.addWidget(self.update)
        buttonLayout.addWidget(self.cancel)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Learning:"))
        layout.addWidget(self.taskName)
        layout.addWidget(QLabel("Language:"))
        layout.addWidget(self.lang)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.descr)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def saveTask(self):
        name = self.taskName.text()
        lang = self.lang.text()
        descr = self.descr.text()
        
        logic.add_learning_task(name, lang, descr)
        
        self.close()
        
    def updateTask(self):
        name = self.taskName.text()
        lang = self.lang.text()
        descr = self.descr.text()
        
        logic.cursor.execute("UPDATE learn SET name = %s, lang = %s, descr = %s WHERE techID = %s",
                              (name, lang, descr, self.taskID))
        logic.db.commit()
        self.close()
        
        
class AddGeneralTaskDialog(QDialog):
    def __init__(self):
        self.taskID = None

        super().__init__()
        self.setWindowTitle("Add General Task")
        self.setMinimumSize(300, 200)
        
        self.taskName = QLineEdit(self)
        self.descr = QLineEdit(self)
        
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.saveTask)
        
        self.update = QPushButton("Update", self)
        self.update.clicked.connect(self.updateTask)
        
        self.cancel = QPushButton("Cancel", self)
        self.cancel.clicked.connect(self.close)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.save)
        buttonLayout.addWidget(self.update)
        buttonLayout.addWidget(self.cancel)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Task Name:"))
        layout.addWidget(self.taskName)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.descr)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def saveTask(self):
        name = self.taskName.text()
        descr = self.descr.text()
        
        logic.add_general_task(name, descr)
        
        self.close()
        
    def updateTask(self):
        name = self.taskName.text()
        descr = self.descr.text()
        
        logic.cursor.execute("UPDATE generalTask SET name = %s, descr = %s WHERE taskID = %s",
                              (name, descr, self.taskID))
        logic.db.commit()
        self.close()
        
