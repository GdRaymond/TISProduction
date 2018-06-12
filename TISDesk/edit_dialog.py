from PyQt5.QtWidgets import QDialog,QTableWidgetItem,QTableWidget,QMessageBox
from PyQt5.QtGui import QFont,QColor
from TISDesk.TIS_edit_dialog import Ui_editDialogShipment
from TISDesk.TIS_edit_order_dialog import Ui_editDialog_Order
from shipments.models import Shipment
from products import size_chart
from TISProduction import tis_log
import datetime
from dateutil import relativedelta

logger=tis_log.get_tis_logger()

class Edit_Dialog_Order(QDialog):
    def __init__(self,parent=None,**kwargs):
        super(Edit_Dialog_Order,self).__init__(parent)
        self.ui=Ui_editDialog_Order()
        self.ui.setupUi(self)
        order_recap1='ID {0} - {1} - {2} - {3} - {4} pcs'.format(kwargs.get('id'),kwargs.get('tis_no')\
                                                    ,kwargs.get('style'),kwargs.get('colour'),kwargs.get('quantity'))
        self.ui.lb_recap_1.setText(order_recap1)
        order_recap2='Made by {0} for client {1}'.format(kwargs.get('supplier'),kwargs.get('client'))
        self.ui.lb_recap_2.setText(order_recap2)
        self.ui.lin_abmno.setText(kwargs.get('abm_no'))
        self.ui.lin_ctm_no.setText(kwargs.get('ctm_no'))
        self.ui.comb_shipment.addItems(kwargs.get('shipments'))
        if kwargs.get('order_date'):
            self.ui.dateE_orderdate.setDate(kwargs.get('order_date'))

        size_show_l=size_chart.get_size_show(kwargs.get('style')) #get the size show list according to style, it is 2-d list
        if not size_show_l: #there is this sytle in the size _show_ need add
            logger.warning(' No this style {} in size show, so not display the size breakup widget'.format(kwargs.get('style')))
            self.ui.groupB_size_1.setTitle('No style {0} in size show ,please add to size_chart.py'.format(kwargs.get('style')))
            self.ui.groupB_size_1.setEnabled(False)
            return

        logger.debug(' get size_show_l for {0}: {1}'.format(kwargs.get('style'),size_show_l))
        size_index_whole=0 #to increase to indicate the size index in all size chart from 1-30, index 0 is total quantity
        for group_no in range(len(size_show_l)): #iterate every group , for shirt only one, for trousers, 2 or 3
            group_box=getattr(self.ui,'groupB_size_{0}'.format(group_no+1))
            group_box.setEnabled(True) #by default the group box size No.2 ,3 are disable, need enable when size group exist
            size_group=size_show_l[group_no]
            logger.debug(' start showing size grou {0}'.format(size_group))
            len_group=len(size_group)
            tableW_group=getattr(self.ui,'tableW_size_{0}'.format(group_no+1)) #dynamicly get the tableWidget to show the group, 1-Regular 2-Stout 3-Long fit
            tableW_group.setColumnCount(len_group)
            tableW_group.setRowCount(2)
            tableW_group.verticalHeader().setVisible(False)
            tableW_group.horizontalHeader().setDefaultSectionSize(49)
            tableW_group.verticalHeader().setDefaultSectionSize(17)
            tableW_group.setRowHeight(0,34)
            tableW_group.setEditTriggers(QTableWidget.CurrentChanged)
            size_title=[]
            for size_no in range(len_group):  #size_no - the index of size in this group
                size_index_whole+=1
                size_title.append(size_group[size_no])
                if size_group[size_no]=='-':
                    tableW_group.setColumnWidth(size_no,1)
                tableW_group.setItem(0,size_no,QTableWidgetItem(str(kwargs.get('size_breakup')[size_index_whole])))
                tableW_group.setItem(1,size_no,QTableWidgetItem('0'))
            tableW_group.setHorizontalHeaderLabels(size_title)
        self.ui.toolBtn_plus_1.clicked.connect(self.add_quantity_group)
        self.ui.toolBtn_plus_2.clicked.connect(self.add_quantity_group)
        self.ui.toolBtn_plus_3.clicked.connect(self.add_quantity_group)

        '''
        self.ui.gridL_size_R.addWidget(self.ui.tableW_size_R)
        for index in range(1,6):
            lb_size=getattr(self.ui,'lb_size_{0}'.format(index))
            lin_size=getattr(self.ui,'lin_size_{0}'.format(index))
            lin_size.setText(str(kwargs.get('size_breakup')[index]))
            self.ui.gridL_size_R.addWidget(lb_size,0,index)
            self.ui.gridL_size_R.addWidget(lin_size, 1, index)
        '''

    def add_quantity_group(self):
        if self.sender() == self.ui.toolBtn_plus_1:
            tableW_size=self.ui.tableW_size_1
            group_no=1
        elif self.sender()==self.ui.toolBtn_plus_2:
            tableW_size = self.ui.tableW_size_2
            group_no = 2
        else:
            tableW_size = self.ui.tableW_size_3
            group_no = 3
        columns=tableW_size.columnCount()
        #self.ui.tableW_size_1.setFont(QFont('SimHei',11,QFont.Bold))
        for index in range(columns):
            try:
                change = int(tableW_size.item(1,index).text())
            except Exception as e:
                logger.error(' not int ')
                continue
            if change!=0:
                logger.debug(
                    ' check group {2} change item{0} :{1}'.format(index, tableW_size.item(1, index).text(), group_no))
                try:
                    origin=int(tableW_size.item(0,index).text())
                    result=origin+change
                    if result<0:
                        tableW_size.item(1,index).setBackground(QColor(202,223,79)) #yellow 255,255,79
                        reply=QMessageBox.information(self,'Warning','Final quantity must not be less than 0',QMessageBox.Ok)
                        continue
                    item=QTableWidgetItem(str(origin+change))
                    item.setForeground(QColor(255, 19, 1))
                    tableW_size.setItem(0,index,item)
                    tableW_size.setItem(1,index,QTableWidgetItem('0'))
                except Exception as e:
                    logger.error(' error calculating quantity :{0}'.format(e))


class Edit_dialog_shipment(QDialog):
    def __init__(self,parent=None,**kwargs):
        super(Edit_dialog_shipment,self).__init__(parent)
        self.ui=Ui_editDialogShipment()
        self.ui.setupUi(self)
        shipment_recap1='ID {0} - {1} - made by {2}'.format(kwargs.get('id','Nil'),kwargs.get('code','Nil'),kwargs.get('Supplier','Nil'))
        self.ui.lb_recap_1.setText(shipment_recap1)
        shipment_recap2='{0} pcs - {1} cartons {2} m3 - {3} kg '.format(kwargs.get('quantity','Nil'),kwargs.get('carton', 'Nil'),kwargs.get('volume','Nil'),kwargs.get('weight','Nil'))
        self.ui.lb_recap_2.setText(shipment_recap2)
        shipment_recap3='in container {0}'.format(kwargs.get('container','Nil'))
        self.ui.lb_recap_3.setText(shipment_recap3)
        if kwargs.get('etd'):
            self.ui.dateE_etd.setDate(kwargs.get('etd'))
        if kwargs.get('eta'):
            self.ui.dateE_eta.setDate(kwargs.get('eta'))
        if kwargs.get('instore'):
            self.ui.dateE_instore.setDate(kwargs.get('instore'))
        if kwargs.get('instore_abm'):
            self.ui.dateE_instore_abm.setDate(kwargs.get('instore_abm'))
        mode_list=[a[0] for a in list(Shipment.MODE) ]
        self.ui.comb_mode.addItems(mode_list)
        self.ui.comb_mode.setCurrentText(str(kwargs.get('mode')))
        etd_port_list=[a[0] for a in list(Shipment.ETD_PORT)]
        self.ui.comb_etdport.addItems(etd_port_list)
        self.ui.comb_etdport.setCurrentText(str(kwargs.get('etd_port')).upper())
        eta_port_list=[a[0] for a in list(Shipment.ETA_PORT)]
        self.ui.comb_etaport.addItems(eta_port_list)
        self.ui.comb_etaport.setCurrentText(str(kwargs.get('eta_port')).upper())

        #below set unvisible for new shipment widget
        self.ui.lb_supplier_new_shipment.setVisible(False)
        self.ui.comb_supplier_new_shipment.setVisible(False)
        self.ui.lb_curentcode_new_shipment.setVisible(False)
        self.ui.listW_currentcode_new_shipment.setVisible(False)
        self.ui.lb_code_new_shipment.setVisible(False)
        self.ui.lin_code_new_shipment.setVisible(False)

class Dialog_New_Shipment(QDialog):
    def __init__(self,parent=None,**kwargs):
        super(Dialog_New_Shipment,self).__init__(parent)
        self.ui=Ui_editDialogShipment()
        self.ui.setupUi(self)
        #below set unvisible for edit_shipment recap label
        self.setWindowTitle('Create New Shipment')
        self.ui.lb_recap.setVisible(False)
        self.ui.lb_recap_1.setVisible(False)
        self.ui.lb_recap_2.setVisible(False)
        self.ui.lb_recap_3.setVisible(False)
        self.ui.dateE_etd.setDate(datetime.date.today())
        self.ui.dateE_eta.setDate(datetime.date.today())
        self.ui.dateE_instore.setDate(datetime.date.today())
        self.ui.dateE_instore_abm.setDate(datetime.date.today())
        mode_list=[a[0] for a in list(Shipment.MODE) ]
        self.ui.comb_mode.addItems(mode_list)
        self.ui.comb_mode.setCurrentText(str(kwargs.get('mode')))
        etd_port_list=[a[0] for a in list(Shipment.ETD_PORT)]
        self.ui.comb_etdport.addItems(etd_port_list)
        self.ui.comb_etdport.setCurrentText(str(kwargs.get('etd_port')).upper())
        eta_port_list=[a[0] for a in list(Shipment.ETA_PORT)]
        self.ui.comb_etaport.addItems(eta_port_list)
        self.ui.comb_etaport.setCurrentText(str(kwargs.get('eta_port')).upper())


        #load supplier
        suppliers=[supplier.get('supplier') for supplier in Shipment.objects.all().order_by('supplier').values('supplier').distinct()]
        logger.debug('get supplier {0}'.format(suppliers))
        self.ui.comb_supplier_new_shipment.addItems(suppliers)
        self.ui.comb_supplier_new_shipment.addItem('--')
        self.ui.comb_supplier_new_shipment.setCurrentText('--')

        self.ui.comb_supplier_new_shipment.currentTextChanged.connect(self.update_widget)
        self.ui.comb_etdport.currentTextChanged.connect(self.update_widget)
        self.ui.comb_mode.currentTextChanged.connect(self.update_widget)
        self.ui.dateE_etd.dateChanged.connect(self.update_widget)




    def update_widget(self):
        logger.debug(' start to update widget')
        #get value form widget
        supplier=self.ui.comb_supplier_new_shipment.currentText().upper()
        mode=self.ui.comb_mode.currentText().upper()
        etd_port=self.ui.comb_etdport.currentText().upper()
        etd_date=self.ui.dateE_etd.date().toPyDate()

        #update eta_date in_store_date
        tt_days=Shipment.get_tt_days(mode,etd_port)
        eta_date=etd_date+relativedelta.relativedelta(days=+tt_days.get('tt_freight'))
        instore_date=eta_date+relativedelta.relativedelta(days=+tt_days.get('tt_cls'))
        self.ui.dateE_eta.setDate(eta_date)
        self.ui.dateE_instore.setDate(instore_date)
        self.ui.dateE_instore_abm.setDate(instore_date)

        #update code and current shipment code
        if self.sender()==self.ui.comb_supplier_new_shipment or self.sender()==self.ui.dateE_etd:
            self.ui.listW_currentcode_new_shipment.clear()
            codes=Shipment.get_current_and_next_shipment_code(supplier,etd_date)
            current_codes=codes.get('current')
            next_shipment_code=codes.get('next')
            if current_codes:
                self.ui.listW_currentcode_new_shipment.addItems(current_codes)
            self.ui.lin_code_new_shipment.setText(next_shipment_code)

    def save_new_shipment(self):
        #get value form widget
        supplier=self.ui.comb_supplier_new_shipment.currentText().upper()
        mode=self.ui.comb_mode.currentText()
        etd_port=self.ui.comb_etdport.currentText().upper()
        etd_date=self.ui.dateE_etd.date().toPyDate()
        eta_date=self.ui.dateE_eta.date().toPyDate()
        instore=self.ui.dateE_instore.date().toPyDate()
        instore_abm=self.ui.dateE_instore_abm.date().toPyDate()
        eta_port=self.ui.comb_etaport.currentText()
        code=self.ui.lin_code_new_shipment.text()
        shipment_dict={'supplier':supplier,'mode':mode,'etd':etd_date,'eta':eta_date,'instore':instore,'instore_abm':instore_abm\
                       ,'code':code,'etd_port':etd_port,'eta_port':eta_port}
        Shipment.objects.create(**shipment_dict)


