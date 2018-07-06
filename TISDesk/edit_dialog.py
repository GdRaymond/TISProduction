from PyQt5.QtWidgets import QDialog,QTableWidgetItem,QTableWidget,QMessageBox
from PyQt5.QtGui import QFont,QColor
from TISDesk.TIS_edit_dialog import Ui_editDialogShipment
from TISDesk.TIS_edit_order_dialog import Ui_editDialog_Order
from TISDesk.TIS_new_order_dialog import Ui_Dialog_New_Order
from shipments.models import Shipment
from orders.models import Order,Product
from products import size_chart,product_price
from TISProduction import tis_log
import datetime
from dateutil import relativedelta
from django.db.models import Count,Min

logger=tis_log.get_tis_logger()


class Dialog_New_Order(QDialog):
    def __init__(self):
        super(Dialog_New_Order,self).__init__()
        self.ui=Ui_Dialog_New_Order()
        self.ui.setupUi(self)
        self.init_data()
        self.ui.comb_supplier.currentTextChanged.connect(self.supplier_on_change)#when connect currentTextChanged, trigger even enter in line_edit
        self.ui.comb_style.currentIndexChanged.connect(self.style_on_change) #when connect currentIndexChanged,only trigger change index

    def init_data(self):
        #load supplier
        suppliers = [supplier.get('supplier') for supplier in Order.objects.order_by().values('supplier').distinct()]
        logger.debug('get supplier {0}'.format(suppliers))
        self.ui.comb_supplier.addItems(suppliers)
        self.ui.comb_supplier.addItem('--')
        self.ui.comb_supplier.setCurrentText('--')

        #load latest tisno
        tis_no_l=Order.objects.all().values('tis_no').distinct()
        if tis_no_l:
            tis_no_max=sorted([item.get('tis_no')[8:12] for item in tis_no_l ])[-1]
        else:
            tis_no_max='4000'
        tis_no='TIS{0}-SO{1}'.format(datetime.date.today().strftime('%y'),int(tis_no_max)+1)
        logger.debug('max tis_no={0}, new tis_no={1}'.format(tis_no_max,tis_no))
        self.ui.lin_tisno.setText(tis_no)

        #load all style_no
        styles=Product.objects.all().values('style_no').distinct()
        if styles:
            style_l=[item.get('style_no') for item in styles]
            #self.ui.comb_style.addItems(style_l)

        #load client
        clients=Order.objects.all().order_by('client').values('client').distinct()
        if clients:
            client_l=[item.get('client') for item in clients]
            self.ui.comb_client.addItems(client_l)

        #set order date
        self.ui.dateE_orderdate.setDate(datetime.date.today())

    def supplier_on_change(self):
        #update shipment combobox
        self.ui.comb_shipment.clear()
        supplier=self.ui.comb_supplier.currentText()
        shipments=Shipment.objects.filter(supplier__iexact=supplier,etd__gt=datetime.date.today())
        shipment_l=[]
        if shipments:
            for shipment in shipments:
                shipment_l.append('{4} - {0} / ETD {1} / {2} / {3}'.format(shipment.code, shipment.etd.strftime('%d-%b'), \
                                                                       shipment.mode, shipment.container, shipment.id))
        self.ui.comb_shipment.addItems(shipment_l)

        #update style combobox, sorted the style frequency
        self.ui.comb_style.clear()
        style_l=[]
        product_in_supplier=Product.objects.filter(order__supplier__iexact=supplier).annotate(c1=Count('order')).order_by('-c1')
        for item in product_in_supplier:
            logger.debug('{0} - count: {1}'.format(item.style_no,item.c1))
            style_l.append(item.style_no)
        product_out_supplier=Product.objects.exclude(order__supplier__iexact=supplier).annotate(c1=Count('order')).order_by('-c1')
        for item in product_out_supplier:
            logger.debug('{0} - count: {1}'.format(item.style_no,item.c1))
            style_l.append(item.style_no)
        self.ui.comb_style.addItems(style_l)

    def style_on_change(self):
        self.ui.tableW_size_1.clear()
        self.ui.tableW_size_2.clear()
        self.ui.groupB_size_2.setEnabled(False)
        self.ui.tableW_size_3.clear()
        self.ui.groupB_size_3.setEnabled(False)
        style=self.ui.comb_style.currentText()
        supplier=self.ui.comb_supplier.currentText()
        if not style or not supplier or supplier=='--':
            return

        #update client and sorted by frequency
        client_l=[]
        client_count=Order.objects.filter(product__style_no__iexact=style).order_by('client').values('client').annotate(count=Count('client')).order_by('-count')
        logger.debug(client_count.query)
        for item in client_count:
            logger.debug(item)
            client_l.append(item.get('client'))
        client_count=Order.objects.exclude(product__style_no__iexact=style).order_by('client').values('client').annotate(count=Count('client')).order_by('-count')
        logger.debug(client_count.query)
        for item in client_count:
            logger.debug(item)
            if item.get('client') not in client_l:
                client_l.append(item.get('client'))
        self.ui.comb_client.clear()
        self.ui.comb_client.addItems(client_l)

        #get colour ever used in order before
        colour_l=product_price.get_colour_list_from_style_supplier(style,supplier)
        if not colour_l:
            logger.error('Can not get the colour list for {0} in product_price'.format(style))
            return

        size_show_l=size_chart.get_size_show(style) #get the size show list according to style, it is 2-d list
        if not size_show_l: #there is this sytle in the size _show_ need add
            logger.warning(' No this style {} in size show, so not display the size breakup widget'.format(style))
            self.ui.groupB_size_1.setTitle('No style {0} in size show ,please add to size_chart.py'.format(style))
            self.ui.groupB_size_1.setEnabled(False)
            return

        logger.debug(' get size_show_l for {0}: {1}'.format(style,size_show_l))
        size_index_whole=0 #to increase to indicate the size index in all size chart from 1-30, index 0 is total quantity
        for group_no in range(len(size_show_l)): #iterate every group , for shirt only one, for trousers, 2 or 3
            group_box=getattr(self.ui,'groupB_size_{0}'.format(group_no+1))
            group_box.setEnabled(True) #by default the group box size No.2 ,3 are disable, need enable when size group exist
            size_group=size_show_l[group_no]
            logger.debug(' start showing size grou {0}'.format(size_group))
            len_group=len(size_group)
            tableW_group=getattr(self.ui,'tableW_size_{0}'.format(group_no+1)) #dynamicly get the tableWidget to show the group, 1-Regular 2-Stout 3-Long fit
            tableW_group.setColumnCount(len_group+1)
            tableW_group.setRowCount(len(colour_l))
            tableW_group.horizontalHeader().setDefaultSectionSize(49)
            tableW_group.setVerticalHeaderLabels([colour for colour in colour_l]) #colour name in vertical title
            tableW_group.setRowHeight(0,34)
            tableW_group.setEditTriggers(QTableWidget.CurrentChanged)
            tableW_group.cellChanged.connect(self.size_quantity_on_change)
            size_title=[]
            for size_no in range(len_group):  #size_no - the index of size in this group
                size_index_whole+=1
                size_title.append(size_group[size_no])
                if size_group[size_no]=='-':
                    tableW_group.setColumnWidth(size_no,1)
                #tableW_group.setItem(0,size_no,QTableWidgetItem(str(kwargs.get('size_breakup')[size_index_whole])))
                #tableW_group.setItem(1,size_no,QTableWidgetItem('0'))
            size_title.append('subtotal')
            tableW_group.setHorizontalHeaderLabels(size_title)

    def size_quantity_on_change(self,row,column):
        logger.debug('sender={0},row={1},column={2}'.format(self.sender(),row,column))
        col_sub_total=self.sender().columnCount()-1
        sub_total=0
        for col_i in range(self.sender().columnCount()-1):
            if not self.sender().item(row,col_i):
                continue
            try:
                cell_value = self.sender().item(row, col_i).text()
                cell_quantity = int(cell_value)
                sub_total += cell_quantity
            except Exception as e:
                logger.error('input is not valid integer')
                self.sender().cellChanged.disconnect(self.size_quantity_on_change)
                self.sender().setItem(row,col_i,QTableWidgetItem(''))
                self.sender().cellChanged.connect(self.size_quantity_on_change)
                continue
        try:
            self.sender().cellChanged.disconnect(self.size_quantity_on_change)
        except Exception as e:
            logger.error('error when disconnnect : {0}'.format(e))
        self.sender().setItem(row,col_sub_total,QTableWidgetItem(str(sub_total)))
        #below update total quantity
        total_quantity=0
        for i in range(1,4):
            group_box=getattr(self.ui,'groupB_size_{0}'.format(i))
            if group_box.isEnabled():
                tableW_size=getattr(self.ui,'tableW_size_{0}'.format(i))
                row_count=tableW_size.rowCount()
                col_count=tableW_size.columnCount()
                for row in range(row_count):
                    if tableW_size.item(row,col_count-1):
                        logger.debug('row0{0} sub-total={1}'.format(row,tableW_size.item(row,col_count-1).text()))
                        total_quantity+=int(tableW_size.item(row,col_count-1).text())
        self.ui.lin_total.setText(str(total_quantity))

        self.sender().cellChanged.connect(self.size_quantity_on_change)

    def save_new_order(self):
        logger.debug('Start to save new order')
        shipment = Shipment.objects.get(id=int(self.ui.comb_shipment.currentText().split('-')[0].strip()))
        product = Product.objects.get(style_no__iexact=self.ui.comb_style.currentText())
        size_show_l = size_chart.get_size_show(product.style_no)
        if not size_show_l:  # below get each size
            logger.warn(' No this style in size show, please add to size_chart.py')
            return
        colours = [self.ui.tableW_size_1.verticalHeaderItem(i).text() for i in
                   range(self.ui.tableW_size_1.rowCount())]
        logger.debug('colours={0}'.format(colours))
        for row, colour in enumerate(colours):
            logger.info('--checking colour {0}'.format(colour))
            order = Order()
            # below get size quantity and change from group size to size breakup size 1-size 31
            size_no_whole = 0
            total_quantity = 0
            for group_no in range(len(size_show_l)):
                size_group = size_show_l[group_no]
                table_w = getattr(self.ui, 'tableW_size_{0}'.format(group_no + 1))
                logger.debug('----saving data {0} to size {1} '.format(table_w, size_group))
                for size_no in range(len(size_group)):
                    size_no_whole += 1
                    if table_w.item(row, size_no) and table_w.item(row, size_no).text():
                        logger.debug('cell text={0}'.format(table_w.item(row, size_no).text()))
                        quantity = int(table_w.item(row, size_no).text())
                        setattr(order, 'size{0}'.format(size_no_whole), quantity)
                if table_w.item(row, len(size_group)) and table_w.item(row, len(size_group)).text():
                    total_quantity += int(table_w.item(row, len(size_group)).text())  # sum for this colour
            # do not save the colour order for 0 quantity
            if total_quantity == 0:
                logger.info('--the colour has no quantity, skip')
                continue
            order.quantity = total_quantity
            order.tis_no = self.ui.lin_tisno.text()
            order.internal_no = self.ui.lin_abmno.text()
            order.ctm_no = self.ui.lin_ctmno.text()
            order.supplier = self.ui.comb_supplier.currentText()
            order.client = self.ui.comb_client.currentText()
            order.product = product
            order.shipment = shipment
            order.colour = colour
            order.order_date = self.ui.dateE_orderdate.date().toPyDate()
            logger.debug('--order info info={0}, quantity={1}'.format(order, order.quantity))
            order.save()
            order.calculate_cartons_volumes()
            logger.debug('--order saved ')


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




