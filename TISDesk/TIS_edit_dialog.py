# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIS_edit_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_editDialogShipment(object):
    def setupUi(self, editDialogShipment):
        editDialogShipment.setObjectName("editDialogShipment")
        editDialogShipment.resize(646, 421)
        self.lb_instoreabm = QtWidgets.QLabel(editDialogShipment)
        self.lb_instoreabm.setGeometry(QtCore.QRect(20, 290, 154, 16))
        self.lb_instoreabm.setObjectName("lb_instoreabm")
        self.lb_etd = QtWidgets.QLabel(editDialogShipment)
        self.lb_etd.setGeometry(QtCore.QRect(20, 170, 61, 16))
        self.lb_etd.setObjectName("lb_etd")
        self.lb_recap = QtWidgets.QLabel(editDialogShipment)
        self.lb_recap.setGeometry(QtCore.QRect(20, 25, 111, 51))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lb_recap.setFont(font)
        self.lb_recap.setObjectName("lb_recap")
        self.lb_etaport = QtWidgets.QLabel(editDialogShipment)
        self.lb_etaport.setGeometry(QtCore.QRect(370, 250, 154, 16))
        self.lb_etaport.setObjectName("lb_etaport")
        self.lb_mode = QtWidgets.QLabel(editDialogShipment)
        self.lb_mode.setGeometry(QtCore.QRect(370, 170, 47, 16))
        self.lb_mode.setObjectName("lb_mode")
        self.lb_etdport = QtWidgets.QLabel(editDialogShipment)
        self.lb_etdport.setGeometry(QtCore.QRect(370, 210, 154, 16))
        self.lb_etdport.setObjectName("lb_etdport")
        self.lb_eta = QtWidgets.QLabel(editDialogShipment)
        self.lb_eta.setGeometry(QtCore.QRect(20, 210, 47, 16))
        self.lb_eta.setObjectName("lb_eta")
        self.lb_instroe = QtWidgets.QLabel(editDialogShipment)
        self.lb_instroe.setGeometry(QtCore.QRect(20, 250, 154, 16))
        self.lb_instroe.setObjectName("lb_instroe")
        self.dateE_etd = QtWidgets.QDateEdit(editDialogShipment)
        self.dateE_etd.setGeometry(QtCore.QRect(100, 170, 110, 22))
        self.dateE_etd.setObjectName("dateE_etd")
        self.comb_mode = QtWidgets.QComboBox(editDialogShipment)
        self.comb_mode.setGeometry(QtCore.QRect(450, 170, 111, 22))
        self.comb_mode.setEditable(False)
        self.comb_mode.setCurrentText("")
        self.comb_mode.setObjectName("comb_mode")
        self.comb_etdport = QtWidgets.QComboBox(editDialogShipment)
        self.comb_etdport.setGeometry(QtCore.QRect(450, 210, 111, 22))
        self.comb_etdport.setObjectName("comb_etdport")
        self.comb_etaport = QtWidgets.QComboBox(editDialogShipment)
        self.comb_etaport.setGeometry(QtCore.QRect(450, 250, 111, 22))
        self.comb_etaport.setObjectName("comb_etaport")
        self.dateE_eta = QtWidgets.QDateEdit(editDialogShipment)
        self.dateE_eta.setGeometry(QtCore.QRect(100, 210, 110, 22))
        self.dateE_eta.setObjectName("dateE_eta")
        self.dateE_instore = QtWidgets.QDateEdit(editDialogShipment)
        self.dateE_instore.setGeometry(QtCore.QRect(100, 250, 110, 22))
        self.dateE_instore.setObjectName("dateE_instore")
        self.dateE_instore_abm = QtWidgets.QDateEdit(editDialogShipment)
        self.dateE_instore_abm.setGeometry(QtCore.QRect(100, 290, 110, 22))
        self.dateE_instore_abm.setObjectName("dateE_instore_abm")
        self.lb_recap_1 = QtWidgets.QLabel(editDialogShipment)
        self.lb_recap_1.setGeometry(QtCore.QRect(140, 30, 481, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lb_recap_1.setFont(font)
        self.lb_recap_1.setObjectName("lb_recap_1")
        self.lb_recap_2 = QtWidgets.QLabel(editDialogShipment)
        self.lb_recap_2.setGeometry(QtCore.QRect(140, 70, 481, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lb_recap_2.setFont(font)
        self.lb_recap_2.setObjectName("lb_recap_2")
        self.lb_recap_3 = QtWidgets.QLabel(editDialogShipment)
        self.lb_recap_3.setGeometry(QtCore.QRect(140, 110, 471, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lb_recap_3.setFont(font)
        self.lb_recap_3.setObjectName("lb_recap_3")
        self.buttonBox = QtWidgets.QDialogButtonBox(editDialogShipment)
        self.buttonBox.setGeometry(QtCore.QRect(400, 370, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(editDialogShipment)
        self.buttonBox.accepted.connect(editDialogShipment.accept)
        self.buttonBox.rejected.connect(editDialogShipment.reject)
        QtCore.QMetaObject.connectSlotsByName(editDialogShipment)

    def retranslateUi(self, editDialogShipment):
        _translate = QtCore.QCoreApplication.translate
        editDialogShipment.setWindowTitle(_translate("editDialogShipment", "Edit Shipment"))
        self.lb_instoreabm.setText(_translate("editDialogShipment", "InStoreABM"))
        self.lb_etd.setText(_translate("editDialogShipment", "ETD"))
        self.lb_recap.setText(_translate("editDialogShipment", "Shipment Recap:"))
        self.lb_etaport.setText(_translate("editDialogShipment", "ETAPort"))
        self.lb_mode.setText(_translate("editDialogShipment", "Mode"))
        self.lb_etdport.setText(_translate("editDialogShipment", "ETDPort"))
        self.lb_eta.setText(_translate("editDialogShipment", "ETA"))
        self.lb_instroe.setText(_translate("editDialogShipment", "InStore"))
        self.lb_recap_1.setText(_translate("editDialogShipment", "Shipment Recap"))
        self.lb_recap_2.setText(_translate("editDialogShipment", "Shipment Recap"))
        self.lb_recap_3.setText(_translate("editDialogShipment", "Shipment Recap"))
