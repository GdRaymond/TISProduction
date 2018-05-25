
from PyQt5.QtWidgets import QMainWindow,QFileDialog,QTableWidgetItem,QAbstractItemView,QDialog,QApplication
from PyQt5.QtGui import QColor,QIcon,QFont
from TISDesk.TIS_mainwindow import Ui_MainWindow
from excelway.tis_excel import TIS_Excel
from products import product_price,size_chart
import os,datetime,time
from PyQt5.QtCore import QThread,pyqtSignal,QDate
from TISProduction import tis_log
from products import views as product_view
from orders import views as order_view
from orders.models import Order
from shipments import views as shipment_view
from shipments.models import Shipment
from PyQt5.QtSql import QSqlRelationalTableModel,QSqlRelation,QSqlRelationalDelegate
from TISDesk.edit_dialog import Edit_dialog_shipment,Edit_Dialog_Order


logger=tis_log.get_tis_logger()


class WorkThread(QThread):
    signal_display=pyqtSignal(dict)

    def __init__(self,job,**kwargs):
        self.job=job
        self.kwargs=kwargs
        logger.debug('work_thread init start for {0}'.format(job))
        super(WorkThread,self).__init__()
        logger.debug('\nwork_thread init end for {0}'.format(job))

    def run(self):
        logger.debug('work_thread start run for {0}'.format(self.job))
        self.signal_display.emit({'msg':'****work_thread start run for {0}'.format(self.job),'level':'INFO'})
        """
        for i in range(5):
            time.sleep(1)
            self.signal_display.emit({'msg':'Already sleep {0} time'.format(i),'level':'DEBUG'})
        """
        if self.job=='init_product':
            product_list=product_price.parse_product(self.signal_display)
            product_price.init_products_db(product_list,self.signal_display)
        elif self.job=='gen_order_trace':
            #order_file = QFileDialog.getOpenFileName(self, 'Open file', os.path.join(os.path.abspath('..'), 'media'))[0]
            order_file=self.kwargs.get('order_file')
            order_list=self.kwargs.get('order_list')
            excel = self.kwargs.get('excel')
            try:
                logger.debug(' read order file in run')
                #order_list=excel.read_order(order_file)
                result = excel.create_from_trace(order_file,order_list, self.signal_display)
            except Exception as e:
                logger.debug(' error occure when read order {0}'.format(e))

        self.signal_display.emit({'msg':'****work_thread finish for {0}'.format(self.job),'level':'INFO'})


class TISMainWindow(QMainWindow):
    def __init__(self,**kwargs):
        super(TISMainWindow,self).__init__(**kwargs)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_open.clicked.connect(self.openfile)
        self.ui.btnTest.clicked.connect(self.test_Excelfuntion)
        self.ui.btnCopy.clicked.connect(self.copy_finance)
        self.ui.btnGeneratePrice.clicked.connect(self.generate_price)
        self.ui.btnRequisition.clicked.connect(self.generate_order_from_requisition)
        self.ui.btnGenerateOrderTrace.clicked.connect(self.create_order_trace)
        self.ui.btnInitProducts.clicked.connect(self.init_products)
        self.ui.btnShowOrder.clicked.connect(self.show_orders)
        self.ui.btnShowShipment.clicked.connect(self.show_shipments)
        self.ui.btnWarehouse.clicked.connect(self.show_shipments_warehouse)
        self.ui.btnInspecSchedule.clicked.connect(self.show_shipments_inspection)
        self.ui.btnCalVol.clicked.connect(self.cal_allshipment_volumes)
        order_title=['Style','TIS','Colour','Quantity','ABM','CTM','OrderDate','PPS','SSS','Report','Cartons','Volume','Weight','3M','id']
        self.ui.tableWOrder.setColumnCount(15)
        self.ui.tableWOrder.setColumnWidth(14,1)
        self.ui.tableWOrder.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWOrder.setHorizontalHeaderLabels(order_title)
        self.ui.tableWOrder.itemDoubleClicked.connect(self.edit_shipment)
        self.ui.btnShipView.clicked.connect(self.show_shipment_view)

    def openfile(self):
        files=QFileDialog.getOpenFileName(self,'Open file','C:\\Users\\rhe\\PyCharm\\TISOrder\\media')
        if files[0]:
            print(files[0])
            self.ui.textBrowser.setTextColor(QColor('red'))
            self.ui.textBrowser.append("{0}-in {1} colour".format(files[0],self.ui.textBrowser.textColor().name()))
            excel=TIS_Excel()
            try:
                l_order=excel.read_order(files[0])
                """
                print(l_order)
                print(len(l_order))
                for row in range(len(l_order)):
                    print('row {0} is'.format(row),end=':')
                    print(l_order[row].values())
                    row_content='/'.join('{0}-{1}'.format(k,v) for k,v in l_order[row].items())
                    print(row_content)
                    self.ui.textBrowser.append(row_content)
                """
                consolidate_order=excel.consolidate_order(l_order)
                print(consolidate_order)
                a=TIS_Excel.dict_to_str(consolidate_order)
                self.ui.textBrowser.append(a)

                l_finance=excel.read_finance()
                print(l_finance)
                consolidate_finance=excel.consolidate_finance(l_finance)
                print(consolidate_finance)
                a=TIS_Excel.dict_to_str(consolidate_finance)
                self.ui.textBrowser.append(a)
                excel.close_wb()
            except Exception as e:
                print('error : {0}'.format(str(e)))


        else:
            print('No')
            self.ui.textBrowser.append("No")

    def display(self,text_dict):
        colour={'DEBUG':'Black','INFO':'Blue','ERROR':'Red'}
        logger.debug(text_dict)
        self.ui.textBrowser.setTextColor(QColor(colour.get(text_dict['level'],'black')))
        self.ui.textBrowser.append(text_dict['msg'])

    def test_Excelfuntion(self):
        files=QFileDialog.getOpenFileName(self,'Open file')
        if files[0]:
            filename=files[0]
            self.ui.textBrowser.append(filename)
            excel=TIS_Excel()
            count_range=excel.test_Excel(filename)
            print(count_range)
            self.ui.textBrowser.append(count_range)

    def copy_finance(self):
        order_file=QFileDialog.getOpenFileName(self,'Open file',os.path.join(os.path.abspath('..'),'media'))[0]
        finance_file=QFileDialog.getOpenFileName(self,'Open file',os.path.join(os.path.abspath('..'),'media'))[0]
        excel=TIS_Excel()
        excel.copy_order_to_finance(order_file,finance_file)
        self.ui.textBrowser.append('finish copy')

    def generate_price(self):
        product_price={}
        finance_file = QFileDialog.getOpenFileName(self, 'Open file', os.path.join(os.path.abspath('..'), 'media'))[0]
        excel=TIS_Excel()
        product_price=excel.generate_product_price(finance_file)
        print(product_price)
        self.ui.textBrowser.append(str(product_price))

    def generate_order_from_requisition(self):
        etd_tanhoo=datetime.datetime(year=2018,month=9,day=20)
        etd_auwin=datetime.datetime(year=2018,month=9,day=18)
        etd_eliel=datetime.datetime(year=2018,month=9,day=17)
        etd_dict={'TANHOO':etd_tanhoo,'AUWIN':etd_auwin,'ELIEL':etd_eliel}
        requisition_path = QFileDialog.getExistingDirectory(self)
        print(requisition_path)
        TIS_Excel.generate_from_requisition(requisition_path,etd_dict)

    def create_order_trace(self):
        order_file=QFileDialog.getOpenFileName(self,'Open file',os.path.join(os.path.abspath('..'),'media'))[0]
        excel=TIS_Excel()
        order_list=excel.read_order(order_file)

        #result=excel.create_from_trace(order_file)
        #self.ui.textBrowser.append('finish creating '+str(result))
        try:
            logger.debug('define WorkThread gen_order_trace')
            self.work_t=WorkThread(job='gen_order_trace',order_file=order_file,order_list=order_list,excel=excel)
            logger.debug('connect signal')
            self.ui.textBrowser.append('connect signal')
            self.work_t.signal_display.connect(self.display)
            logger.debug('Start work_thread gen_order_trace')
            self.ui.textBrowser.append('Start work_thread gen_order_trace')
            self.work_t.start()
        except Exception as e:
            logger.debug(' error occur using thread gen_order_trace {0}'.format(e))
        try:
            self.close_wb()
        except Exception as e:
            print(e)


    def init_products(self):
        #product_list=product_price.parse_product()
        #product_price.init_products_db(product_list)
        try:
            logger.debug('define WorkThread init_product')
            self.work_t=WorkThread(job='init_product')
            logger.debug('connect singal')
            self.ui.textBrowser.append('connect signal')
            self.work_t.signal_display.connect(self.display)
            logger.debug('Start work_thread')
            self.ui.textBrowser.append('Start work_thread init_product')
            self.work_t.start()
        except Exception as e:
            logger.debug(' error occur using thread init_product {0}'.format(e))

    def append_one_order(self,order):
        row_pos=self.ui.tableWOrder.rowCount()
        #logger.debug('Row Position is {0}'.format(row_pos))
        self.ui.tableWOrder.insertRow(row_pos)
        self.ui.tableWOrder.setRowHeight(row_pos, 30)
        self.ui.tableWOrder.setFont(QFont('Segoe UI', 9))
        self.ui.tableWOrder.setItem(row_pos,0,QTableWidgetItem(order.product.style_no))
        self.ui.tableWOrder.setItem(row_pos,1,QTableWidgetItem(order.tis_no))
        self.ui.tableWOrder.setItem(row_pos,2, QTableWidgetItem(order.colour))
        self.ui.tableWOrder.setItem(row_pos,3,QTableWidgetItem(str(order.quantity)) )
        self.ui.tableWOrder.setItem(row_pos,4,QTableWidgetItem(order.internal_no))
        self.ui.tableWOrder.setItem(row_pos,5,QTableWidgetItem(order.ctm_no))
        self.ui.tableWOrder.setItem(row_pos,6,QTableWidgetItem(order.order_date.strftime('%d %b %y')) )
        self.ui.tableWOrder.setItem(row_pos,7,QTableWidgetItem('-'))
        self.ui.tableWOrder.setItem(row_pos,8,QTableWidgetItem('-') )
        self.ui.tableWOrder.setItem(row_pos,9,QTableWidgetItem('-') )
        self.ui.tableWOrder.setItem(row_pos,10,QTableWidgetItem(str(order.cartons)) )
        self.ui.tableWOrder.setItem(row_pos,11,QTableWidgetItem(str(order.volumes)) )
        self.ui.tableWOrder.setItem(row_pos,12,QTableWidgetItem(str(order.weights)) )
        self.ui.tableWOrder.setItem(row_pos,13,QTableWidgetItem(str(order.tape_no)) )
        self.ui.tableWOrder.setItem(row_pos,14,QTableWidgetItem(str(order.id)) )

    def append_one_shipment(self,shipment,flag_all_order='F'):
        row_pos=self.ui.tableWOrder.rowCount()
        logger.debug('Row Position is {0}'.format(row_pos))
        self.ui.tableWOrder.insertRow(row_pos)
        try:
            self.ui.tableWOrder.setSpan(row_pos,0,1,14)
            self.ui.tableWOrder.setRowHeight(row_pos,50)
            self.ui.tableWOrder.setFont(QFont('SimHei',11,QFont.Bold))
        except Exception as e:
            logger.error(' error occur when set row height and font {0}'.format(e))
        shipment_info='{0}-{1}-From {2} to {3}, ETD:{4} ETA:{5} Delivery:{6}; {7} with {8} cartons {9}m3 {10}kg'.format(
            shipment.supplier,shipment.code,shipment.etd_port,shipment.eta_port,shipment.etd,shipment.eta,shipment.instore,
            shipment.container,shipment.cartons,shipment.volume,shipment.weight
        )
        logger.debug('  shipment_info is {0}'.format(shipment_info))
        try:
            newItem=QTableWidgetItem(shipment_info)
            newItem.setBackground(QColor(76, 190, 230)) #blue  grey:131,149,147 green:129,215,65
            newItem.setFont(QFont('SimHei',11,QFont.Bold))
            #newItem.setTextColor(QColor(200, 111, 100))
            self.ui.tableWOrder.setItem(row_pos,0,newItem)
            self.ui.tableWOrder.setItem(row_pos, 14, QTableWidgetItem(str(shipment.id)))

        except Exception as e:
            logger.error(' error when set new Item {0}'.format(e))
        try:
            if flag_all_order=='F':  #'F' - get all orders in this shipment
                orders=shipment.order_set.all()
            elif flag_all_order=='I': #'I' - for Mike inspection
                orders=shipment_view.get_orders_inspection_from_shipment(shipment)
                if not orders or len(orders)==0:
                    newItem = QTableWidgetItem(shipment_info)
                    newItem.setBackground(QColor(131, 149, 147))  # blue  grey:131,149,147 green:129,215,65 red:255,19,1
                    newItem.setFont(QFont('SimHei', 11, QFont.Bold))
                    # newItem.setTextColor(QColor(200, 111, 100))
                    self.ui.tableWOrder.setItem(row_pos, 0, newItem)

            logger.debug(' get orders from shipment {0}'.format(len(orders)))
            for order in orders:
                self.append_one_order(order)
        except Exception as e:
            logger.error('  error when get orders from shipment {0}'.format(e))


    def show_orders(self):
        self.ui.tableWOrder.setRowCount(0)
        orders=order_view.get_orders()
        logger.debug(' Get orders {0}'.format(len(orders)))
        #self.ui.tableWOrder.setRowCount(len(orders))
        for index in range(len(orders)):
            order=orders[index]
            logger.debug('  start to show order {0}/{1}/{2}'.format(order.tis_no,order.product.style_no,order.quantity))
            try:
                self.append_one_order(order)
            except Exception as e:
                logger.error(' error occurs when show order in Table widget {0}'.format(e))

    def show_shipments(self):
        self.ui.tableWOrder.setRowCount(0)
        shipments=shipment_view.get_all_shipment()
        logger.debug(' Get shipments {0}'.format(len(shipments)))
        for shipment in shipments:
            logger.debug('  start to show shipment {0}'.format(shipment))
            self.append_one_shipment(shipment)

    def show_shipments_warehouse(self):
        self.ui.tableWOrder.setRowCount(0)
        shipments=shipment_view.get_next_month_warehouse()
        logger.debug(' Get warehouse shipments {0}'.format(len(shipments)))
        for shipment in shipments:
            logger.debug('  start to show shipment {0}'.format(shipment))
            self.append_one_shipment(shipment)
        shipment_view.write_all_shipment_warehouse(shipments)

    def show_shipments_inspection(self):
        self.ui.tableWOrder.setRowCount(0)
        shipments=shipment_view.get_next_month_inspection()
        logger.debug('  get inspection shipments {0}'.format(len(shipments)))
        for shipment in shipments:
            logger.debug('  start to show shipment {0}'.format(shipment))
            self.append_one_shipment(shipment,'I')
        shipment_view.write_inspection_shipment(shipments)



    def cal_allshipment_volumes(self):
        logger.info('start to cal all order cartons volumes')
        try:
            Order.calculate_allorder_cartons()
            shipment_view.cal_all_shipment_volume()
        except Exception as e:
            logger.error('error when cal all shipment vol {0}'.format(e))



    def show_shipment_view(self):
        try:
            self.model=QSqlRelationalTableModel(self)
            self.model.setTable(Shipment)
            self.ui.tableVshipment.setModel(self.model)
            delegate=QSqlRelationalDelegate(self.ui.tableVshipment)
            self.ui.tableVshipment.setItemDelegate(delegate)
        except Exception as e:
            logger.error('error occur when show shipment view : {0}'.format(e))

    def edit_shipment(self,item):
        try:
            logger.debug('table widget double clicked {0}-{1}-{2}-{3}-{4}'.format(item.row(),item.column(),item.text()
                     ,self.ui.tableWOrder.item(item.row(),14).text(),self.ui.tableWOrder.item(item.row(),0).text()))
        except Exception as e:
            logger.error('error occur when get id at last coloum-{0}'.format(e))
        record_id=int(self.ui.tableWOrder.item(item.row(),14).text())
        if self.ui.tableWOrder.item(item.row(),1): #in order line the col 1 is TIS no, not none
            #handle order form
            order=Order.objects.get(id=record_id)
            shipments=Shipment.objects.filter(supplier__iexact=order.supplier,eta__gt=datetime.date.today())\
                .exclude(order__id=order.id).order_by('-etd')
            shipment_l=['{4} - {0} / ETD {1} / {2} / {3}'.format(order.shipment.code,order.shipment.etd.strftime('%d-%b'),\
                                                    order.shipment.mode,order.shipment.container,order.shipment.id)]
            #assemble shipment list
            for shipment in shipments:
                shipment_l.append('{4} - {0} / ETD {1} / {2} / {3}'.format(shipment.code,shipment.etd.strftime('%d-%b'),\
                                                    shipment.mode,shipment.container,shipment.id))
             #assemble size_breakup
            size_breakup=[0] #there are 31 items, item 0 is total quantity, item 1 is size 1 quantity...
            for index in range(1,30):
                quantity=getattr(order,'size{0}'.format(index),0)
                size_breakup[0]+=quantity
                size_breakup.append(quantity)
            logger.debug('got size breakup {0}'.format(size_breakup))

            #assemble **kwargs
            order_dict={'id':order.id,'style':order.product.style_no,'shipments':shipment_l,'tis_no':order.tis_no,\
                        'supplier':order.supplier,'client':order.client,'abm_no':order.internal_no,'quantity':order.quantity, \
                        'colour':order.colour,'order_date':order.order_date,'size_breakup':size_breakup,'ctm_no':order.ctm_no}
            logger.debug(' start to edit order {0}'.format(order))
            try:
                dialog=Edit_Dialog_Order(**order_dict)
                action=dialog.exec_()
                if action:
                    logger.debug('dialog order exec_:{0}'.format(action))
                    logger.debug('order saving ')
                    order.internal_no=dialog.ui.lin_abmno.text()
                    order.ctm_no=dialog.ui.lin_ctm_no.text()
                    order.order_date=dialog.ui.dateE_orderdate.date().toPyDate()
                    shipment_id=int(dialog.ui.comb_shipment.currentText().strip().split('-')[0])
                    shipment=Shipment.objects.get(id=shipment_id)
                    order.shipment=shipment
                    #below saving the size break up
                    size_show_l=size_chart.get_size_show(order.product.style_no)
                    size_no_whole=0
                    for group_no in range(len(size_show_l)):
                        size_group=size_show_l[group_no]
                        table_w=getattr(dialog.ui,'tableW_size_{0}'.format(group_no+1))
                        logger.debug('start to save data {0} to size {1} '.format(table_w,size_group))
                        for size_no in range(len(size_group)):
                            size_no_whole+=1
                            quantity=int(table_w.item(0,size_no).text())
                            setattr(order,'size{0}'.format(size_no_whole),quantity)

                    order.save()
                    logger.debug('order saved {0}-{1}-{2}-{3}'.format(order,order.shipment,order.internal_no,order.ctm_no))
                else:
                    logger.debug('dialog order not exec_')
            except Exception as e:
                logger.error('error saving order: {0}'.format(e))

        else: # None for shipment line
            shipment=Shipment.objects.get(id=record_id)
            shipment_dict={'id':record_id,'etd':shipment.etd,'eta':shipment.eta,'instore':shipment.instore,
                           'instore_abm':shipment.instore_abm,'quantity':shipment.total_quantity,'volume':shipment.volume,
                           'carton':shipment.cartons,'etd_port':shipment.etd_port,'eta_port':shipment.eta_port,
                           'container':shipment.container,'mode':shipment.mode,'code':shipment.code,'weight':shipment.weight,
                           'supplier':shipment.supplier}
            logger.debug(' start to edit shipment {0}'.format(shipment))
            try:
                dialog=Edit_dialog_shipment(**shipment_dict)
                action=dialog.exec_()
                if action:
                    logger.debug('dialog exec_ : {0}'.format(action))
                    logger.debug('shipment saving {0} -{1} -{2} -{3} -{4} -{5} -{6} -{7}'.format(shipment,dialog.ui.dateE_etd.date(),\
                                dialog.ui.dateE_eta.date(),dialog.ui.dateE_instore.date(),dialog.ui.dateE_instore_abm.date, \
                                dialog.ui.comb_etdport.currentText(),dialog.ui.comb_etaport.currentText(),dialog.ui.comb_mode.currentText()))
                    shipment.etd=dialog.ui.dateE_etd.date().toPyDate()
                    shipment.eta=dialog.ui.dateE_eta.date().toPyDate()
                    shipment.instore=dialog.ui.dateE_instore.date().toPyDate()
                    shipment.instore_abm=dialog.ui.dateE_instore_abm.date().toPyDate()
                    shipment.etd_port=dialog.ui.comb_etdport.currentText()
                    shipment.eta_port=dialog.ui.comb_etaport.currentText()
                    shipment.mode=dialog.ui.comb_mode.currentText()
                    shipment.save()
                    logger.debug('shipment saved {0} -{1} -{2} -{3} -{4} -{5} -{6} -{7}'.format(shipment,shipment.etd,
                                                                                                shipment.eta,shipment.instore,
                                                                                                shipment.instore_abm,shipment.etd_port,
                                                                                                shipment.eta_port,shipment.mode))
                else:
                    logger.debug('dialog not exec_')
                dialog.destroy()
            except Exception as e:
                logger.error(' error dialog {0}'.format(e))
        QApplication.processEvents()