from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QIcon
import pymongo
import re
import random
from policy_parser import parse
from mongo_connection import db
from executor import Executor
from enforce import Enforcer
from rollback import Rollbacker
import admin

if not admin.isUserAdmin():
  admin.runAsAdmin()


class UiMainWindow(QWidget):
  def init(self, db):
    self.checkedLines = []
    self.allLines = []
    self.notPassed = []
    self.isCheckedAll = False
    self.db = db
    self.policy = None
    self.name = None
    self.table2Index = 0
    self.enforced = []
    self.executor = Executor()
    self.enforcer = Enforcer()
    self.rollbacker = Rollbacker()

  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(1000, 500)
    self.initMainWindow(MainWindow)
    self.initHeader(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def initPoliciesTable(self):
    self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
    self.tableWidget.setGeometry(QtCore.QRect(30, 45, 320, 300))
    self.tableWidget.setColumnCount(1)
    self.tableWidget.setHorizontalHeaderItem(0,  QTableWidgetItem("POLICIES"))
    header = self.tableWidget.horizontalHeader() 
    self.tableWidget.cellClicked.connect(self.tableClicked)   
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

  def initSaveAsButton(self):
    self.btnAction = QtWidgets.QPushButton(self.centralwidget)
    self.btnAction.setGeometry(QtCore.QRect(650, 350, 90, 30))
    self.btnAction.setObjectName("btnAction")
    self.btnAction.clicked.connect(self.add_policy)
      
      
  def initTextEdit(self):
    self.tableWidget2 = QtWidgets.QTableWidget(self.centralwidget)
    self.tableWidget2.setGeometry(QtCore.QRect(370, 45, 580, 300))
    self.tableWidget2.setColumnCount(2)
    self.tableWidget2.setHorizontalHeaderItem(0,  QTableWidgetItem("SELECT"))
    header = self.tableWidget2.horizontalHeader()       
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

  def initPushButton(self, MainWindow):
    self.pushBtn = QtWidgets.QPushButton(MainWindow)
    self.pushBtn.setText("Search Now")
    self.pushBtn.move(750, 30)
    self.pushBtn.setStyleSheet("background-color:rgba(255,100,255,0.2)")
    self.pushBtn.clicked.connect(self.searchFunction)

  def initSearchBar(self, MainWindow):
    self.searchBar = QtWidgets.QTextEdit(MainWindow)
    self.searchBar.setGeometry(QtCore.QRect(550, 30, 200, 30) )
    self.searchBar.setStyleSheet("background-color:white")

  def initCheckAllBtn(self, MainWindow):
    self.checkAllBtn = QtWidgets.QPushButton(MainWindow)
    self.checkAllBtn.setText("Check All")
    self.checkAllBtn.move(370, 30)
    self.checkAllBtn.setStyleSheet("background-color:rgba(255,100,255,0.2)")
    self.checkAllBtn.clicked.connect(self.checkAll)

  def initBackSearchBtn(self, MainWindow):
    self.backSearchBtn = QtWidgets.QPushButton(MainWindow)
    self.backSearchBtn.setText("Back to all")
    self.backSearchBtn.move(850, 30)
    self.backSearchBtn.setStyleSheet("background-color:rgba(255,100,255,0.2)")
    self.backSearchBtn.clicked.connect(self.backFromSearch)

  def initSaveButton(self, MainWindow):
    self.saveBtn = QtWidgets.QPushButton(MainWindow)
    self.saveBtn.setText("Save")
    self.saveBtn.move(500, 370)
    self.saveBtn.clicked.connect(self.save)
    self.saveBtn.setEnabled(False)

  def initExecuteButton(self, MainWindow):
    self.executeBtn = QtWidgets.QPushButton(MainWindow)
    self.executeBtn.setText("Execute")
    self.executeBtn.move(850, 370)
    self.executeBtn.clicked.connect(self.execute)
    self.executeBtn.setEnabled(False)

  def initEnforceButton(self, MainWindow):
    self.enforceBtn = QtWidgets.QPushButton(MainWindow)
    self.enforceBtn.setText("Enforce")
    self.enforceBtn.move(850, 400)
    self.enforceBtn.clicked.connect(self.enforce)
    self.enforceBtn.setEnabled(False)

  def initRollbackButton(self, MainWindow):
    self.rollbackBtn = QtWidgets.QPushButton(MainWindow)
    self.rollbackBtn.setText("Rollback")
    self.rollbackBtn.move(850, 430)
    self.rollbackBtn.clicked.connect(self.rollback)
    self.rollbackBtn.setEnabled(False)

  def initMainWindow(self, MainWindow):
    self.centralwidget = QtWidgets.QWidget(MainWindow)
    self.centralwidget.setObjectName("centralwidget")
    self.initTextEdit()
    self.initSaveAsButton()
    self.initSaveButton(MainWindow)
    self.initExecuteButton(MainWindow)
    self.initEnforceButton(MainWindow)
    self.initRollbackButton(MainWindow)
    self.initPoliciesTable()
    self.initSearchBar(MainWindow)
    self.initPushButton(MainWindow)
    self.initCheckAllBtn(MainWindow)
    self.initBackSearchBtn(MainWindow)
    MainWindow.setCentralWidget(self.centralwidget)

  def initMenubar(self, MainWindow):
    self.menubar = QtWidgets.QMenuBar(MainWindow)
    self.menubar.setGeometry(QtCore.QRect(0, 0, 514, 21))
    self.menubar.setObjectName("menubar")
    self.menuFile = QtWidgets.QMenu(self.menubar)
    self.menuFile.setObjectName("menuFile")
    MainWindow.setMenuBar(self.menubar)

  def initFileImport(self, MainWindow):
    self.actionOpenFile = QtWidgets.QAction(MainWindow)
    self.actionOpenFile.setObjectName("actionOpenFile")
    self.actionOpenFile.setShortcut('Ctrl+O')
    self.actionOpenFile.triggered.connect(self.fileOpen)
    self.menuFile.addAction(self.actionOpenFile)
    self.menubar.addAction(self.menuFile.menuAction())

  def initHeader(self, MainWindow):
    self.initMenubar(MainWindow)
    self.initFileImport(MainWindow)
    self.retranslateUi(MainWindow)

  def retranslateUi(self, MainWindow):
    _translate = QtCore.QCoreApplication.translate
    MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    self.btnAction.setText(_translate("MainWindow", "Save as"))
    self.menuFile.setTitle(_translate("MainWindow", "Import Policy"))
    self.actionOpenFile.setText(_translate("MainWindow", "Open File"))

  def enforce(self):
    self.enforceBtn.setEnabled(False)
    self.rollbackBtn.setEnabled(True)
    for policy in self.notPassed:
      if policy not in self.enforced:
        res = self.enforcer.enforce(policy)
        if res["status"] == 0:
          self.enforced.append({"policy": policy, "val": res["msg"]})
    self.notPassed = []
    self.execute()



  def rollback(self):
    for policy in self.enforced:
      self.rollbacker.rollback(policy["policy"], policy["val"])
    self.rollbackBtn.setEnabled(False)
    self.enforced = []
    self.execute()

  def execute(self):
    self.enforceBtn.setEnabled(True)
    self.executeBtn.setEnabled(False)
    policies = db.find_policy_by_name(self.name)["policy"]
    self.clearTable()
    for policy in policies:
            self.tableWidget2.insertRow(self.table2Index)
            self.tableWidget2.setItem(self.table2Index, 0, QtWidgets.QTableWidgetItem(policy["description"]))
            result = self.executor.execute(policy)
            color = "green" if result["status"] == 0 else "blue" if result["status"] == -1 else "red"
            self.tableWidget2.setItem(self.table2Index, 1, QtWidgets.QTableWidgetItem(result["msg"]))
            self.tableWidget2.item(self.table2Index, 1).setBackground(QtGui.QColor(color))
            self.table2Index += 1
            if result["status"] == 1:
              self.notPassed.append(policy)

  def save(self):
    self.checkedLines = []
    self.addCheckedLines()
    policy = self.getNewPolicyFile(self.policy) 
    db.update_policy_by_name(self.name, policy)
    self.clearTable()
    self.saveBtn.setEnabled(False)

  def checkAll(self):
    res = []
    for row in range(self.tableWidget2.rowCount()): 
      _item = self.tableWidget2.item(row, 0) 
      if _item:            
        item0 = self.tableWidget2.item(row, 0)
        if self.isCheckedAll:       
          item0.setCheckState(QtCore.Qt.Unchecked)
        else:
          item0.setCheckState(QtCore.Qt.Checked)
    self.isCheckedAll = not self.isCheckedAll

  def addCheckedLines(self):
    for row in range(self.tableWidget2.rowCount()): 
      _item = self.tableWidget2.item(row, 0) 
      if _item:            
        item0 = self.tableWidget2.item(row, 0)
        if item0.checkState() > 0:
          description = self.tableWidget2.item(row, 1).text()
          if description not in self.checkedLines:
            self.checkedLines.append(description)

  def updateCheckedLines(self):
    self.btnAction.setEnabled(True)
    for row in range(self.tableWidget2.rowCount()): 
      _item = self.tableWidget2.item(row, 0) 
      if _item:            
        item0 = self.tableWidget2.item(row, 0)
        description = self.tableWidget2.item(row, 1).text()
        if item0.checkState() > 0:
          if description not in self.checkedLines:
            self.checkedLines.append(description)
        else:
          if description in self.checkedLines:
            self.checkedLines.remove(description)

  def backFromSearch(self):
    self.updateCheckedLines()
    self.table2Index = 0
    self.tableWidget2.setRowCount(0)

    for line in self.allLines:
      self.tableWidget2.insertRow(self.table2Index)
      chkBoxItem = QTableWidgetItem()
      chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
      if line in self.checkedLines:
        chkBoxItem.setCheckState(QtCore.Qt.Checked)
      else:
        chkBoxItem.setCheckState(QtCore.Qt.Unchecked) 
      self.tableWidget2.setItem(self.table2Index, 0, chkBoxItem)
      self.tableWidget2.setItem(self.table2Index, 1, QtWidgets.QTableWidgetItem(line))
      self.table2Index += 1

  def addRow2SearchTable(self, index, line):
    self.tableWidget2.insertRow(index)
    chkBoxItem = QTableWidgetItem()
    chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
    if line in self.checkedLines:
      chkBoxItem.setCheckState(QtCore.Qt.Checked)
    else:
      chkBoxItem.setCheckState(QtCore.Qt.Unchecked) 
    self.tableWidget2.setItem(index, 0, chkBoxItem)
    self.tableWidget2.setItem(index, 1, QtWidgets.QTableWidgetItem(line))
          
  def searchFunction(self):
    self.btnAction.setEnabled(False)
    self.checkedLines = []
    self.addCheckedLines()
    self.tableWidget2.setRowCount(0)

    index = 0
    query = self.searchBar.toPlainText().strip()
    for line in self.allLines:
      if query.lower() in line.lower():
        self.addRow2SearchTable(index, line)
        index += 1
  
  def getPolicyName(self):
    text, okPressed = QInputDialog.getText(self, "Get text","Your name:", QLineEdit.Normal, "")
    if okPressed and text != '':
      return text

  def parsePolicy(self, text):
    return parse(text)

  def addRow2table(self, name):
    rowPosition = self.tableWidget.rowCount()
    self.tableWidget.insertRow(rowPosition)
    item = QtWidgets.QTableWidgetItem(name)
    self.tableWidget.setItem(rowPosition, 0, item)

  def iteratePolicy(self, parsed):
    for value in parsed:
        self.parseCustomItem(value)
        self.table2Index += 1

  def parseCustomItem(self, val):
        self.tableWidget2.insertRow(self.table2Index)
        chkBoxItem = QTableWidgetItem()
        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(QtCore.Qt.Unchecked) 
        self.tableWidget2.setItem(self.table2Index, 0, chkBoxItem)
        self.tableWidget2.setItem(self.table2Index, 1, QtWidgets.QTableWidgetItem(f'{val["description"]}  TYPE: {val["type"]}'))
        self.allLines.append(f'{val["description"]}  TYPE: {val["type"]}')

  def clearTable(self):
    self.table2Index = 0
    self.allLines = []
    self.checkedLines = []
    self.tableWidget2.setRowCount(0)

  def tableClicked(self, row, column):
    self.executeBtn.setEnabled(True)
    self.saveBtn.setEnabled(True)
    self.clearTable()
    name = self.tableWidget.item(row, column).text()
    self.name = name
    policy = self.db.find_policy_by_name(name)["policy"]
    self.policy = policy
    self.iteratePolicy(policy)


  def fileOpen(self):
    name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', options=QtWidgets.QFileDialog.DontUseNativeDialog)
    file = open(name, 'r')
    self.clearTable()
    
    with file:
      text = file.read()
      parsedPolicy = self.parsePolicy(text)
      self.policy = parsedPolicy
      self.iteratePolicy(parsedPolicy)              

  def getPolicies(self):
    policies = db.get_all_policies_name()
    for policy in policies:
      self.addRow2table(policy["name"])

  def getNewPolicy(self, value, description):
    for attr in value["body"]:
      if attr["name"] == "description":
        if attr["value"] == description:
          return value


  def getNewPolicyFile(self, policy):
    res = []
    for description in self.checkedLines:
      for val in policy:
        param_description = description.split("  TYPE:")[0]
        if param_description == val["description"]:
          res.append(val)
    return res

  def add_policy(self):
    self.checkedLines = []
    self.addCheckedLines()
    name = self.getPolicyName()
    policy = self.getNewPolicyFile(self.policy) 
    self.db.insert_policy(policy, name)
    self.addRow2table(name)
    self.clearTable()
        

if __name__ == "__main__":
  if admin.isUserAdmin():
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.init(db)
    ui.setupUi(MainWindow)
    ui.getPolicies()
    MainWindow.show()
    sys.exit(app.exec_())
