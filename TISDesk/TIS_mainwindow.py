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
        self.tabShipment = QtWidgets.QTabWidget(self.centralwidget)
        self.tabShipment.setGeometry(QtCore.QRect(0, 0, 1341, 661))
        self.tabShipment.setObjectName("tabShipment")
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
        self.btnCopy.setGeometry(QtCore.QRect(450, 10, 91, 23))
        self.btnCopy.setObjectName("btnCopy")
        self.btnRequisition = QtWidgets.QPushButton(self.tab)
        self.btnRequisition.setGeometry(QtCore.QRect(370, 10, 75, 23))
        self.btnRequisition.setObjectName("btnRequisition")
        self.btnGenerateOrderTrace = QtWidgets.QPushButton(self.tab)
        self.btnGenerateOrderTrace.setGeometry(QtCore.QRect(90, 10, 101, 23))
        self.btnGenerateOrderTrace.setObjectName("btnGenerateOrderTrace")
        self.btnInitProducts = QtWidgets.QPushButton(self.tab)
        self.btnInitProducts.setGeometry(QtCore.QRect(10, 10, 75, 23))
        self.btnInitProducts.setObjectName("btnInitProducts")
        self.btnCalVol = QtWidgets.QPushButton(self.tab)
        self.btnCalVol.setGeometry(QtCore.QRect(190, 10, 81, 23))
        self.btnCalVol.setObjectName("btnCalVol")
        self.btn_load_bak_packinglist = QtWidgets.QPushButton(self.tab)
        self.btn_load_bak_packinglist.setGeometry(QtCore.QRect(550, 10, 91, 23))
        self.btn_load_bak_packinglist.setObjectName("btn_load_bak_packinglist")
        self.tabShipment.addTab(self.tab, "")
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
        self.tabShipment.addTab(self.tab_2, "")
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
        self.tabShipment.addTab(self.editShipment, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_7)
        self.groupBox_3.setGeometry(QtCore.QRect(300, 20, 301, 301))
        self.groupBox_3.setObjectName("groupBox_3")
        self.btnAuwinSplit = QtWidgets.QPushButton(self.groupBox_3)
        self.btnAuwinSplit.setGeometry(QtCore.QRect(20, 260, 271, 23))
        self.btnAuwinSplit.setObjectName("btnAuwinSplit")
        self.comb_shipment_auwin_origin = QtWidgets.QComboBox(self.groupBox_3)
        self.comb_shipment_auwin_origin.setGeometry(QtCore.QRect(90, 20, 151, 22))
        self.comb_shipment_auwin_origin.setObjectName("comb_shipment_auwin_origin")
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 81, 16))
        self.label_9.setObjectName("label_9")
        self.listW_allshipment_au = QtWidgets.QListWidget(self.groupBox_3)
        self.listW_allshipment_au.setGeometry(QtCore.QRect(10, 90, 111, 151))
        self.listW_allshipment_au.setObjectName("listW_allshipment_au")
        self.label_10 = QtWidgets.QLabel(self.groupBox_3)
        self.label_10.setGeometry(QtCore.QRect(10, 60, 81, 16))
        self.label_10.setObjectName("label_10")
        self.listW_targetshipment_au = QtWidgets.QListWidget(self.groupBox_3)
        self.listW_targetshipment_au.setGeometry(QtCore.QRect(180, 90, 111, 151))
        self.listW_targetshipment_au.setObjectName("listW_targetshipment_au")
        self.label_11 = QtWidgets.QLabel(self.groupBox_3)
        self.label_11.setGeometry(QtCore.QRect(200, 60, 81, 16))
        self.label_11.setObjectName("label_11")
        self.toolB_move_shipment_to_target = QtWidgets.QToolButton(self.groupBox_3)
        self.toolB_move_shipment_to_target.setGeometry(QtCore.QRect(130, 120, 41, 19))
        self.toolB_move_shipment_to_target.setObjectName("toolB_move_shipment_to_target")
        self.toolB_move_shipment_to_all = QtWidgets.QToolButton(self.groupBox_3)
        self.toolB_move_shipment_to_all.setGeometry(QtCore.QRect(130, 170, 41, 19))
        self.toolB_move_shipment_to_all.setObjectName("toolB_move_shipment_to_all")
        self.toolB_refresh_shipment_auwin = QtWidgets.QToolButton(self.groupBox_3)
        self.toolB_refresh_shipment_auwin.setGeometry(QtCore.QRect(250, 10, 41, 41))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("refresh.PNG"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolB_refresh_shipment_auwin.setIcon(icon1)
        self.toolB_refresh_shipment_auwin.setIconSize(QtCore.QSize(51, 41))
        self.toolB_refresh_shipment_auwin.setObjectName("toolB_refresh_shipment_auwin")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_7)
        self.groupBox_4.setGeometry(QtCore.QRect(30, 20, 241, 80))
        self.groupBox_4.setObjectName("groupBox_4")
        self.btn_new_shipment = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_new_shipment.setGeometry(QtCore.QRect(30, 30, 191, 23))
        self.btn_new_shipment.setObjectName("btn_new_shipment")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_7)
        self.groupBox_5.setGeometry(QtCore.QRect(620, 20, 451, 291))
        self.groupBox_5.setObjectName("groupBox_5")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setGeometry(QtCore.QRect(10, 20, 41, 16))
        self.label_12.setObjectName("label_12")
        self.comb_shipmenttool_supplier = QtWidgets.QComboBox(self.groupBox_5)
        self.comb_shipmenttool_supplier.setGeometry(QtCore.QRect(50, 20, 71, 22))
        self.comb_shipmenttool_supplier.setObjectName("comb_shipmenttool_supplier")
        self.comb_shipmenttool_shipment = QtWidgets.QComboBox(self.groupBox_5)
        self.comb_shipmenttool_shipment.setGeometry(QtCore.QRect(190, 20, 251, 22))
        self.comb_shipmenttool_shipment.setObjectName("comb_shipmenttool_shipment")
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setGeometry(QtCore.QRect(140, 20, 51, 16))
        self.label_13.setObjectName("label_13")
        self.btn_shipmenttool_getshipmentorderinfo = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_getshipmentorderinfo.setGeometry(QtCore.QRect(20, 60, 81, 31))
        self.btn_shipmenttool_getshipmentorderinfo.setObjectName("btn_shipmenttool_getshipmentorderinfo")
        self.btn_shipmenttool_checkbooking = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_checkbooking.setGeometry(QtCore.QRect(140, 60, 131, 31))
        self.btn_shipmenttool_checkbooking.setObjectName("btn_shipmenttool_checkbooking")
        self.btn_shipmenttool_checktestreport = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_checktestreport.setGeometry(QtCore.QRect(320, 60, 121, 31))
        self.btn_shipmenttool_checktestreport.setObjectName("btn_shipmenttool_checktestreport")
        self.btn_shipmenttool_checkdocument = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_checkdocument.setGeometry(QtCore.QRect(320, 100, 121, 31))
        self.btn_shipmenttool_checkdocument.setObjectName("btn_shipmenttool_checkdocument")
        self.btn_shipmenttool_checkinvoice = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_checkinvoice.setGeometry(QtCore.QRect(170, 100, 121, 31))
        self.btn_shipmenttool_checkinvoice.setObjectName("btn_shipmenttool_checkinvoice")
        self.btn_shipmenttool_checkpackinglist = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_shipmenttool_checkpackinglist.setGeometry(QtCore.QRect(20, 100, 121, 31))
        self.btn_shipmenttool_checkpackinglist.setObjectName("btn_shipmenttool_checkpackinglist")
        self.tabShipment.addTab(self.tab_7, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_6.setGeometry(QtCore.QRect(20, 20, 251, 161))
        self.groupBox_6.setObjectName("groupBox_6")
        self.btn_new_order = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_new_order.setGeometry(QtCore.QRect(30, 30, 191, 23))
        self.btn_new_order.setObjectName("btn_new_order")
        self.tabShipment.addTab(self.tab_3, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1364, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabShipment.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TIS Production Manage"))
        self.btn_open.setText(_translate("MainWindow", "OpenFile"))
        self.btnTest.setText(_translate("MainWindow", "TestButton"))
        self.btnCopy.setText(_translate("MainWindow", "CopyToFinance"))
        self.btnRequisition.setText(_translate("MainWindow", "Requisition"))
        self.btnGenerateOrderTrace.setText(_translate("MainWindow", "2-GenOrderTrace"))
        self.btnInitProducts.setText(_translate("MainWindow", "1-InitProduct"))
        self.btnCalVol.setText(_translate("MainWindow", "3-CalAllVolum"))
        self.btn_load_bak_packinglist.setText(_translate("MainWindow", "LoadBakPacking"))
        self.tabShipment.setTabText(self.tabShipment.indexOf(self.tab), _translate("MainWindow", "System"))
        self.btnShowOrder.setText(_translate("MainWindow", "ShowAllOrder"))
        self.btnShowShipment.setText(_translate("MainWindow", "ShowAllShipment"))
        self.btnWarehouse.setText(_translate("MainWindow", "WarehouseSchedule"))
        self.btnInspecSchedule.setText(_translate("MainWindow", "InspectionSchedule"))
        self.groupBox.setTitle(_translate("MainWindow", "Search"))
        self.lin_search.setToolTip(_translate("MainWindow", "i.e. RM1050 Yel/Nav"))
        self.lin_search.setStatusTip(_translate("MainWindow", "i.e. RM1050 Yel/Nav"))
        self.btnSearch.setText(_translate("MainWindow", "Search"))
        self.tabShipment.setTabText(self.tabShipment.indexOf(self.tab_2), _translate("MainWindow", "ReadOrder"))
        self.groupBox_2.setTitle(_translate("MainWindow", "TestReport"))
        self.label.setText(_translate("MainWindow", "Supplier"))
        self.label_2.setText(_translate("MainWindow", "Fabric"))
        self.label_3.setText(_translate("MainWindow", "Colour"))
        self.label_4.setText(_translate("MainWindow", "Approved"))
        self.btn_checkorder.setToolTip(_translate("MainWindow", "get the order Instore Date later than today for selected colour"))
        self.btn_checkorder.setText(_translate("MainWindow", "CheckOrder"))
        self.label_5.setText(_translate("MainWindow", "Report No."))
        self.label_6.setText(_translate("MainWindow", "Comment"))
        self.label_7.setText(_translate("MainWindow", "Rejected"))
        self.label_8.setText(_translate("MainWindow", "Select"))
        self.btn_save_testreport.setText(_translate("MainWindow", "Save Test Report"))
        self.tabShipment.setTabText(self.tabShipment.indexOf(self.editShipment), _translate("MainWindow", "SampleCheck"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Auwin Split"))
        self.btnAuwinSplit.setText(_translate("MainWindow", "SplitAuwinShipment"))
        self.label_9.setText(_translate("MainWindow", "Origin shipment"))
        self.label_10.setText(_translate("MainWindow", "All shipment"))
        self.label_11.setText(_translate("MainWindow", "Target shipment"))
        self.toolB_move_shipment_to_target.setText(_translate("MainWindow", ">>>>"))
        self.toolB_move_shipment_to_all.setText(_translate("MainWindow", "<<<<"))
        self.toolB_refresh_shipment_auwin.setText(_translate("MainWindow", "..."))
        self.groupBox_4.setTitle(_translate("MainWindow", "New Shipment"))
        self.btn_new_shipment.setText(_translate("MainWindow", "CreateNewShipment"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Shipment Tool"))
        self.label_12.setText(_translate("MainWindow", "Supplier"))
        self.label_13.setText(_translate("MainWindow", "Shipment"))
        self.btn_shipmenttool_getshipmentorderinfo.setToolTip(_translate("MainWindow", "Get the shipment order No. container and ETD , copy to clipboard for email paste"))
        self.btn_shipmenttool_getshipmentorderinfo.setText(_translate("MainWindow", "Get OrderIno"))
        self.btn_shipmenttool_checkbooking.setToolTip(_translate("MainWindow", "Compare the booking spreadsheet with shipment order, copy difference to clipboard for email"))
        self.btn_shipmenttool_checkbooking.setText(_translate("MainWindow", "Check Shipment Booking"))
        self.btn_shipmenttool_checktestreport.setToolTip(_translate("MainWindow", "<html><head/><body><p>Check outstanding test report for selected shipment, including no report and rejected report</p></body></html>"))
        self.btn_shipmenttool_checktestreport.setText(_translate("MainWindow", "Check TestReport"))
        self.btn_shipmenttool_checkdocument.setToolTip(_translate("MainWindow", "Compare the booking spreadsheet with shipment order, copy difference to clipboard for email"))
        self.btn_shipmenttool_checkdocument.setText(_translate("MainWindow", "Check ShipDocument"))
        self.btn_shipmenttool_checkinvoice.setToolTip(_translate("MainWindow", "Compare the booking spreadsheet with shipment order, copy difference to clipboard for email"))
        self.btn_shipmenttool_checkinvoice.setText(_translate("MainWindow", "Check Invoice Only"))
        self.btn_shipmenttool_checkpackinglist.setToolTip(_translate("MainWindow", "Compare the booking spreadsheet with shipment order, copy difference to clipboard for email"))
        self.btn_shipmenttool_checkpackinglist.setText(_translate("MainWindow", "Check PackingList Only"))
        self.tabShipment.setTabText(self.tabShipment.indexOf(self.tab_7), _translate("MainWindow", "Shipment"))
        self.groupBox_6.setTitle(_translate("MainWindow", "New Order"))
        self.btn_new_order.setText(_translate("MainWindow", "CreateNewOrder-Manually"))
        self.tabShipment.setTabText(self.tabShipment.indexOf(self.tab_3), _translate("MainWindow", "Order"))

