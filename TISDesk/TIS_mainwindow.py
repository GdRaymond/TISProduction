# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIS_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1364, 695)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("TIS.PNG"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 1341, 661))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab)
        self.textBrowser.setGeometry(QtCore.QRect(10, 40, 1311, 591))
        self.textBrowser.setObjectName("textBrowser")
        self.btn_open = QtWidgets.QPushButton(self.tab)
        self.btn_open.setGeometry(QtCore.QRect(20, 10, 75, 23))
        self.btn_open.setObjectName("btn_open")
        self.btnTest = QtWidgets.QPushButton(self.tab)
        self.btnTest.setGeometry(QtCore.QRect(740, 10, 75, 23))
        self.btnTest.setObjectName("btnTest")
        self.btnCopy = QtWidgets.QPushButton(self.tab)
        self.btnCopy.setGeometry(QtCore.QRect(120, 10, 75, 23))
        self.btnCopy.setObjectName("btnCopy")
        self.btnGeneratePrice = QtWidgets.QPushButton(self.tab)
        self.btnGeneratePrice.setGeometry(QtCore.QRect(210, 10, 81, 23))
        self.btnGeneratePrice.setObjectName("btnGeneratePrice")
        self.btnRequisition = QtWidgets.QPushButton(self.tab)
        self.btnRequisition.setGeometry(QtCore.QRect(300, 10, 75, 23))
        self.btnRequisition.setObjectName("btnRequisition")
        self.btnGenerateOrderTrace = QtWidgets.QPushButton(self.tab)
        self.btnGenerateOrderTrace.setGeometry(QtCore.QRect(380, 10, 91, 23))
        self.btnGenerateOrderTrace.setObjectName("btnGenerateOrderTrace")
        self.btnInitProducts = QtWidgets.QPushButton(self.tab)
        self.btnInitProducts.setGeometry(QtCore.QRect(480, 10, 75, 23))
        self.btnInitProducts.setObjectName("btnInitProducts")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1364, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TIS Tools"))
        self.btn_open.setText(_translate("MainWindow", "OpenFile"))
        self.btnTest.setText(_translate("MainWindow", "TestButton"))
        self.btnCopy.setText(_translate("MainWindow", "CopyFinance"))
        self.btnGeneratePrice.setText(_translate("MainWindow", "GeneratePrice"))
        self.btnRequisition.setText(_translate("MainWindow", "Requisition"))
        self.btnGenerateOrderTrace.setText(_translate("MainWindow", "GenOrderTrace"))
        self.btnInitProducts.setText(_translate("MainWindow", "InitProduct"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "ReadOrder"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))

