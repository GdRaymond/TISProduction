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
        self.tabSampleCheck = QtWidgets.QTabWidget(self.centralwidget)
        self.tabSampleCheck.setGeometry(QtCore.QRect(0, 0, 1341, 661))
        self.tabSampleCheck.setObjectName("tabSampleCheck")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab)
        self.textBrowser.setGeometry(QtCore.QRect(10, 40, 1311, 591))
        self.textBrowser.setObjectName("textBrowser")
        self.btn_open = QtWidgets.QPushButton(self.tab)
        self.btn_open.setGeometry(QtCore.QRect(660, 10, 75, 23))
        self.btn_open.setObjectName("btn_open")
        self.btnTest = QtWidgets.QPushButton(self.tab)
        self.btnTest.setGeometry(QtCore.QRect(740, 10, 75, 23))
        self.btnTest.setObjectName("btnTest")
        self.btnCopy = QtWidgets.QPushButton(self.tab)
        self.btnCopy.setGeometry(QtCore.QRect(460, 10, 75, 23))
        self.btnCopy.setObjectName("btnCopy")
        self.btnGeneratePrice = QtWidgets.QPushButton(self.tab)
        self.btnGeneratePrice.setGeometry(QtCore.QRect(10, 10, 81, 23))
        self.btnGeneratePrice.setObjectName("btnGeneratePrice")
        self.btnRequisition = QtWidgets.QPushButton(self.tab)
        self.btnRequisition.setGeometry(QtCore.QRect(380, 10, 75, 23))
        self.btnRequisition.setObjectName("btnRequisition")
        self.btnGenerateOrderTrace = QtWidgets.QPushButton(self.tab)
        self.btnGenerateOrderTrace.setGeometry(QtCore.QRect(170, 10, 91, 23))
        self.btnGenerateOrderTrace.setObjectName("btnGenerateOrderTrace")
        self.btnInitProducts = QtWidgets.QPushButton(self.tab)
        self.btnInitProducts.setGeometry(QtCore.QRect(90, 10, 75, 23))
        self.btnInitProducts.setObjectName("btnInitProducts")
        self.btnCalVol = QtWidgets.QPushButton(self.tab)
        self.btnCalVol.setGeometry(QtCore.QRect(260, 10, 75, 23))
        self.btnCalVol.setObjectName("btnCalVol")
        self.tabSampleCheck.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tableWOrder = QtWidgets.QTableWidget(self.tab_2)
        self.tableWOrder.setGeometry(QtCore.QRect(0, 50, 1331, 581))
        self.tableWOrder.setRowCount(0)
        self.tableWOrder.setColumnCount(15)
        self.tableWOrder.setObjectName("tableWOrder")
        self.btnShowOrder = QtWidgets.QPushButton(self.tab_2)
        self.btnShowOrder.setGeometry(QtCore.QRect(10, 10, 75, 23))
        self.btnShowOrder.setObjectName("btnShowOrder")
        self.btnShowShipment = QtWidgets.QPushButton(self.tab_2)
        self.btnShowShipment.setGeometry(QtCore.QRect(100, 10, 81, 23))
        self.btnShowShipment.setObjectName("btnShowShipment")
        self.btnWarehouse = QtWidgets.QPushButton(self.tab_2)
        self.btnWarehouse.setGeometry(QtCore.QRect(190, 10, 111, 23))
        self.btnWarehouse.setObjectName("btnWarehouse")
        self.btnInspecSchedule = QtWidgets.QPushButton(self.tab_2)
        self.btnInspecSchedule.setGeometry(QtCore.QRect(310, 10, 111, 23))
        self.btnInspecSchedule.setObjectName("btnInspecSchedule")
        self.groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox.setGeometry(QtCore.QRect(670, 0, 361, 48))
        self.groupBox.setObjectName("groupBox")
        self.lin_search = QtWidgets.QLineEdit(self.groupBox)
        self.lin_search.setGeometry(QtCore.QRect(20, 20, 231, 20))
        self.lin_search.setObjectName("lin_search")
        self.btnSearch = QtWidgets.QPushButton(self.groupBox)
        self.btnSearch.setGeometry(QtCore.QRect(270, 20, 75, 23))
        self.btnSearch.setObjectName("btnSearch")
        self.tabSampleCheck.addTab(self.tab_2, "")
        self.editShipment = QtWidgets.QWidget()
        self.editShipment.setObjectName("editShipment")
        self.groupBox_2 = QtWidgets.QGroupBox(self.editShipment)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 10, 871, 251))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(10, 20, 47, 13))
        self.label.setObjectName("label")
        self.comb_supplier = QtWidgets.QComboBox(self.groupBox_2)
        self.comb_supplier.setGeometry(QtCore.QRect(60, 20, 71, 22))
        self.comb_supplier.setObjectName("comb_supplier")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(140, 20, 41, 16))
        self.label_2.setObjectName("label_2")
        self.comb_fabric = QtWidgets.QComboBox(self.groupBox_2)
        self.comb_fabric.setGeometry(QtCore.QRect(170, 20, 451, 22))
        self.comb_fabric.setObjectName("comb_fabric")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(10, 90, 47, 13))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(0, 150, 47, 13))
        self.label_4.setObjectName("label_4")
        self.tableW_colour = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableW_colour.setGeometry(QtCore.QRect(50, 90, 811, 121))
        self.tableW_colour.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.tableW_colour.setFont(font)
        self.tableW_colour.setRowCount(3)
        self.tableW_colour.setColumnCount(20)
        self.tableW_colour.setObjectName("tableW_colour")
        self.tableW_colour.horizontalHeader().setDefaultSectionSize(40)
        self.tableW_colour.verticalHeader().setVisible(False)
        self.btn_checkorder = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_checkorder.setGeometry(QtCore.QRect(40, 220, 121, 23))
        self.btn_checkorder.setObjectName("btn_checkorder")
        self.lin_testreport_ref = QtWidgets.QLineEdit(self.groupBox_2)
        self.lin_testreport_ref.setGeometry(QtCore.QRect(60, 60, 121, 20))
        self.lin_testreport_ref.setObjectName("lin_testreport_ref")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(10, 60, 51, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(190, 60, 47, 13))
        self.label_6.setObjectName("label_6")
        self.lin_testreport_comment = QtWidgets.QLineEdit(self.groupBox_2)
        self.lin_testreport_comment.setGeometry(QtCore.QRect(240, 60, 381, 20))
        self.lin_testreport_comment.setObjectName("lin_testreport_comment")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(0, 180, 47, 13))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setGeometry(QtCore.QRect(10, 120, 31, 16))
        self.label_8.setObjectName("label_8")
        self.btn_save_testreport = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_save_testreport.setGeometry(QtCore.QRect(180, 220, 121, 23))
        self.btn_save_testreport.setObjectName("btn_save_testreport")
        self.tableW_samplecheck_order = QtWidgets.QTableWidget(self.editShipment)
        self.tableW_samplecheck_order.setGeometry(QtCore.QRect(10, 270, 1291, 361))
        self.tableW_samplecheck_order.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.tableW_samplecheck_order.setFont(font)
        self.tableW_samplecheck_order.setRowCount(0)
        self.tableW_samplecheck_order.setColumnCount(15)
        self.tableW_samplecheck_order.setObjectName("tableW_samplecheck_order")
        self.tableW_samplecheck_order.horizontalHeader().setDefaultSectionSize(100)
        self.tableW_samplecheck_order.verticalHeader().setVisible(False)
        self.tableW_samplecheck_order.verticalHeader().setHighlightSections(True)
        self.tabSampleCheck.addTab(self.editShipment, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1364, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabSampleCheck.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TIS Production Manage"))
        self.btn_open.setText(_translate("MainWindow", "OpenFile"))
        self.btnTest.setText(_translate("MainWindow", "TestButton"))
        self.btnCopy.setText(_translate("MainWindow", "CopyFinance"))
        self.btnGeneratePrice.setText(_translate("MainWindow", "GeneratePrice"))
        self.btnRequisition.setText(_translate("MainWindow", "Requisition"))
        self.btnGenerateOrderTrace.setText(_translate("MainWindow", "GenOrderTrace"))
        self.btnInitProducts.setText(_translate("MainWindow", "InitProduct"))
        self.btnCalVol.setText(_translate("MainWindow", "CalAllVolum"))
        self.tabSampleCheck.setTabText(self.tabSampleCheck.indexOf(self.tab), _translate("MainWindow", "System"))
        self.btnShowOrder.setText(_translate("MainWindow", "ShowAllOrder"))
        self.btnShowShipment.setText(_translate("MainWindow", "ShowAllShipment"))
        self.btnWarehouse.setText(_translate("MainWindow", "WarehouseSchedule"))
        self.btnInspecSchedule.setText(_translate("MainWindow", "InspectionSchedule"))
        self.groupBox.setTitle(_translate("MainWindow", "Search"))
        self.lin_search.setToolTip(_translate("MainWindow", "i.e. RM1050 Yel/Nav"))
        self.lin_search.setStatusTip(_translate("MainWindow", "i.e. RM1050 Yel/Nav"))
        self.btnSearch.setText(_translate("MainWindow", "Search"))
        self.tabSampleCheck.setTabText(self.tabSampleCheck.indexOf(self.tab_2), _translate("MainWindow", "ReadOrder"))
        self.groupBox_2.setTitle(_translate("MainWindow", "TestReport"))
        self.label.setText(_translate("MainWindow", "Supplier"))
        self.label_2.setText(_translate("MainWindow", "Fabric"))
        self.label_3.setText(_translate("MainWindow", "Colour"))
        self.label_4.setText(_translate("MainWindow", "Approved"))
        self.btn_checkorder.setText(_translate("MainWindow", "CheckOrder"))
        self.label_5.setText(_translate("MainWindow", "Report No."))
        self.label_6.setText(_translate("MainWindow", "Comment"))
        self.label_7.setText(_translate("MainWindow", "Rejected"))
        self.label_8.setText(_translate("MainWindow", "Select"))
        self.btn_save_testreport.setText(_translate("MainWindow", "Save Test Report"))
        self.tabSampleCheck.setTabText(self.tabSampleCheck.indexOf(self.editShipment), _translate("MainWindow", "SampleCheck"))

