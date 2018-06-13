
from PyQt5.QtWidgets import QMainWindow,QFileDialog,QTableWidgetItem,QAbstractItemView,QDialog,QApplication,\
    QMessageBox,QButtonGroup,QCheckBox,QRadioButton,QAbstractScrollArea,QListWidgetItem
from PyQt5.QtGui import QColor,QIcon,QFont
from TISDesk.TIS_mainwindow import Ui_MainWindow
from excelway.tis_excel import TIS_Excel
from products import product_price,size_chart
from products.models import Product
import os,datetime,time,re
from PyQt5.QtCore import QThread,pyqtSignal,QDate,Qt
from TISProduction import tis_log
from products import views as product_view
from orders import views as order_view
from orders.models import Order,FabricTrim,SampleCheck
from shipments import views as shipment_view
from shipments.models import Shipment
from PyQt5.QtSql import QSqlRelationalTableModel,QSqlRelation,QSqlRelationalDelegate
from TISDesk.edit_dialog import Edit_dialog_shipment,Edit_Dialog_Order,Dialog_New_Shipment
from core import fts_search
from TISDesk import clipboard


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
        #self.ui.btnGeneratePrice.clicked.connect(self.generate_price)
        self.ui.btnRequisition.clicked.connect(self.generate_order_from_requisition)
        self.ui.btnGenerateOrderTrace.clicked.connect(self.create_order_trace)
        self.ui.btnInitProducts.clicked.connect(self.init_products)
        self.ui.btnShowOrder.clicked.connect(self.show_all_orders)
        self.ui.btnShowShipment.clicked.connect(self.show_all_shipments)
        self.ui.btnWarehouse.clicked.connect(self.show_shipments_warehouse)
        self.ui.btnInspecSchedule.clicked.connect(self.show_shipments_inspection)
        self.ui.btnCalVol.clicked.connect(self.cal_allshipment_volumes)
        order_title=['Style','TIS','Colour','Quantity','ABM','CTM','OrderDate','PPS','SSS','Report','Cartons','Volume','Weight','3M','id']
        self.ui.tableWOrder.setColumnCount(15)
        self.ui.tableWOrder.setColumnWidth(14,1)
        self.ui.tableWOrder.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWOrder.setHorizontalHeaderLabels(order_title)
        self.ui.tableWOrder.itemDoubleClicked.connect(self.edit_shipment)
        self.ui.btnSearch.clicked.connect(self.full_text_search)
        self.ui.btn_checkorder.clicked.connect(self.check_orders)
        self.load_initial_data()
        self.ui.comb_supplier.currentTextChanged.connect(self.load_comb_fabric)
        self.ui.comb_fabric.currentTextChanged.connect(self.load_fabric_colour)
        self.ui.tableW_colour.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        sample_check_order_title=['Select','TIS','Style','Colour','Quantity','CTM','OrderDate','Report','PPS','SSS','Cartons','Volume','Weight','3M','id']
        self.ui.tableW_samplecheck_order.setHorizontalHeaderLabels(sample_check_order_title)
        self.ui.tableW_samplecheck_order.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents) #in PyQt5 allow to adjust to cotent
        self.ui.btn_save_testreport.clicked.connect(self.save_test_report)
        self.ui.btnAuwinSplit.clicked.connect(self.split_shipment_aw)
        self.ui.toolB_refresh_shipment_auwin.clicked.connect(self.refresh_shipment_au_split)
        self.ui.comb_shipment_auwin_origin.currentTextChanged.connect(self.reload_shipment_au_split)
        self.ui.toolB_move_shipment_to_target.clicked.connect(self.shipment_selected_move)
        self.ui.toolB_move_shipment_to_all.clicked.connect(self.shipment_selected_move)
        self.ui.btn_new_shipment.clicked.connect(self.creat_new_shipment)
        self.ui.comb_shipmenttool_supplier.currentTextChanged.connect(self.load_shipment_from_supplier)
        self.ui.btn_shipmenttool_getshipmentorderinfo.clicked.connect(self.shipment_tool_getorderinfo)
        self.ui.btn_shipmenttool_checkbooking.clicked.connect(self.check_shipment_booking)


    def load_initial_data(self):
        suppliers=[supplier.get('supplier') for supplier in Order.objects.order_by().values('supplier').distinct()]
        logger.debug( 'get suppliers list {0}'.format(suppliers))
        self.ui.comb_supplier.addItems(suppliers)
        self.ui.comb_shipmenttool_supplier.addItems(suppliers)
        self.ui.comb_supplier.addItem('--')
        self.ui.comb_shipmenttool_supplier.addItem('--')
        self.ui.comb_supplier.setCurrentText('--')
        self.ui.comb_shipmenttool_supplier.setCurrentText('--')

    def load_comb_fabric(self):
        self.ui.comb_fabric.clear()
        supplier=self.ui.comb_supplier.currentText()
        #products=Order.objects.filter(supplier__iexact=supplier).order_by().values('product').distinct()
        try:
            fabrics_dict=Product.objects.filter(order__supplier=supplier).values('fabric__nickname').order_by().distinct()
            logger.debug(' get products list {0}'.format(fabrics_dict))
            fabrics=[fabric.get('fabric__nickname') for fabric in fabrics_dict]
            fabrics.sort()
        except Exception as e:
            logger.error(' error when get fabric: {0}'.format(e))
        self.ui.comb_fabric.addItems(fabrics)
        self.ui.comb_fabric.addItem('--')
        self.ui.comb_fabric.setCurrentText('--')

    def load_fabric_colour(self):
        supplier = self.ui.comb_supplier.currentText()
        fabric=self.ui.comb_fabric.currentText()
        try:
            order_id_dict=Product.objects.filter(fabric__nickname=fabric).values('order__supplier','order__id').filter(order__supplier=supplier).order_by().distinct()
            order_id_list=[order_id.get('order__id') for order_id in order_id_dict]
            logger.debug(' get order id list {0}'.format(order_id_list))
            colour_dict=Order.objects.filter(id__in=order_id_list).values('fabrictrim__colour_solid').order_by().distinct()
            colours=[colour.get('fabrictrim__colour_solid') for colour in colour_dict]
            #logger.debug(' get colour list {0}'.format(colours))
            colours_len=len(colours)
            self.ui.tableW_colour.setColumnCount(colours_len)
            for i in range(colours_len):
                colour=colours[i]
                item=QTableWidgetItem(colour)
                item.setToolTip(colour)
                self.ui.tableW_colour.setHorizontalHeaderItem(i,item)
                #below add the check box and radio box to widget
                qcheck=QCheckBox()
                setattr(self.ui,'checkB_{0}'.format(colour),qcheck)
                qradio_app=QRadioButton()
                qradio_app.setChecked(True)
                setattr(self.ui,'radioB_a_{0}'.format(colour),qradio_app)
                qradio_rej=QRadioButton()
                setattr(self.ui,'radioB_r_{0}'.format(colour),qradio_rej)
                qbutton_group=QButtonGroup()
                setattr(self.ui,'buttonG_{0}'.format(colour),qbutton_group)
                qbutton_group.addButton(qradio_app)
                qbutton_group.addButton(qradio_rej)

                self.ui.tableW_colour.setCellWidget(0,i,qcheck)
                self.ui.tableW_colour.setCellWidget(1,i,qradio_app)
                self.ui.tableW_colour.setCellWidget(2,i,qradio_rej)


        except Exception as e:
            logger.error(' error when get colour :{0}'.format(e))
        self.ui.tableW_colour.resizeColumnsToContents()


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
        order_file=QFileDialog.getOpenFileName(self,'Please select latest Order Trace spreadsheet',os.path.join(os.path.abspath('..'),'media'))[0]
        finance_file=QFileDialog.getOpenFileName(self,'Please select latest Finance spreadsheet',os.path.join(os.path.abspath('..'),'media'))[0]
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
        order_file=QFileDialog.getOpenFileName(self,'Please select latest Order Trace spreadsheet',os.path.join(os.path.abspath('..'),'media'))[0]
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
        pp_comments = ''
        pp_checks=order.samplecheck_set.filter(type__iexact='p')
        if pp_checks:
            logger.debug('get pp_checks quantity {0}'.format(len(pp_checks)))
            pp_comments=pp_checks[0].comment
            for pp_check in range(1,len(pp_checks)):
                pp_comments='{0}\n{1}'.format(pp_comments,pp_check.comment)
        self.ui.tableWOrder.setItem(row_pos,7,QTableWidgetItem(pp_comments))
        ss_comments = ''
        ss_checks=order.samplecheck_set.filter(type__iexact='s')
        if ss_checks:
            logger.debug('get ss_checks quantity {0}'.format(len(ss_checks)))
            ss_comments=ss_checks[0].comment
            for ss_check in range(1,len(ss_checks)):
                ss_comments='{0}\n{1}'.format(ss_comments,ss_check.comment)
        self.ui.tableWOrder.setItem(row_pos,8,QTableWidgetItem(ss_comments) )
        test_comments = ''
        test_checks=order.samplecheck_set.filter(type__iexact='t')
        if test_checks:
            logger.debug('get test_checks quantity {0}'.format(len(test_checks)))
            test_comments='{0}-{1}-{2}'.format(test_checks[0].check_date,test_checks[0].ref,test_checks[0].comment)
            for i in range(1,len(test_checks)):
                test_comments='{0}\n{1}-{2}-{3}'.format(test_comments,test_checks[i].check_date,test_checks[i].ref,test_checks[i].comment)
        self.ui.tableWOrder.setItem(row_pos,9,QTableWidgetItem(test_comments) )
        self.ui.tableWOrder.setItem(row_pos,10,QTableWidgetItem(str(order.cartons)) )
        self.ui.tableWOrder.setItem(row_pos,11,QTableWidgetItem(str(order.volumes)) )
        self.ui.tableWOrder.setItem(row_pos,12,QTableWidgetItem(str(order.weights)) )
        self.ui.tableWOrder.setItem(row_pos,13,QTableWidgetItem(str(order.tape_no)) )
        self.ui.tableWOrder.setItem(row_pos,14,QTableWidgetItem(str(order.id)) )

    def append_samplecheck_one_order(self,order):
        row_pos=self.ui.tableW_samplecheck_order.rowCount()
        #logger.debug('Row Position is {0}'.format(row_pos))
        self.ui.tableW_samplecheck_order.insertRow(row_pos)
        self.ui.tableW_samplecheck_order.setRowHeight(row_pos, 30)
        self.ui.tableW_samplecheck_order.setFont(QFont('Segoe UI', 9))
        check_box=QCheckBox()
        setattr(self.ui,'checkB_samplecheck_order_{0}'.format(row_pos),check_box)
        self.ui.tableW_samplecheck_order.setCellWidget(row_pos,0,check_box)
        self.ui.tableW_samplecheck_order.setItem(row_pos,1,QTableWidgetItem(order.tis_no))
        self.ui.tableW_samplecheck_order.setItem(row_pos,2, QTableWidgetItem(order.product.style_no))
        self.ui.tableW_samplecheck_order.setItem(row_pos,3,QTableWidgetItem(order.colour) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,4,QTableWidgetItem(str(order.quantity)))
        self.ui.tableW_samplecheck_order.setItem(row_pos,5,QTableWidgetItem(order.ctm_no))
        self.ui.tableW_samplecheck_order.setItem(row_pos,6,QTableWidgetItem(order.order_date.strftime('%d %b %y')) )
        pp_comments = ''
        pp_checks=order.samplecheck_set.filter(type__iexact='p')
        if pp_checks:
            logger.debug('get pp_checks quantity {0}'.format(len(pp_checks)))
            pp_comments=pp_checks[0].comment
            for pp_check in range(1,len(pp_checks)):
                pp_comments='{0}\n{1}'.format(pp_comments,pp_check.comment)
        self.ui.tableW_samplecheck_order.setItem(row_pos,8,QTableWidgetItem(pp_comments))
        ss_comments = ''
        ss_checks=order.samplecheck_set.filter(type__iexact='s')
        if ss_checks:
            logger.debug('get ss_checks quantity {0}'.format(len(ss_checks)))
            ss_comments=ss_checks[0].comment
            for ss_check in range(1,len(ss_checks)):
                ss_comments='{0}\n{1}'.format(ss_comments,ss_check.comment)
        self.ui.tableW_samplecheck_order.setItem(row_pos,9,QTableWidgetItem(ss_comments) )
        test_comments = ''
        test_checks=order.samplecheck_set.filter(type__iexact='t')
        if test_checks:
            logger.debug('get test_checks quantity {0}'.format(len(test_checks)))
            test_comments='{0}-{1}-{2}'.format(test_checks[0].check_date,test_checks[0].ref,test_checks[0].comment)
            for i in range(1,len(test_checks)):
                test_comments='{0}\n{1}-{2}-{3}'.format(test_comments,test_checks[i].check_date,test_checks[i].ref,test_checks[i].comment)
        self.ui.tableW_samplecheck_order.setItem(row_pos,7,QTableWidgetItem(test_comments) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,10,QTableWidgetItem(str(order.cartons)) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,11,QTableWidgetItem(str(order.volumes)) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,12,QTableWidgetItem(str(order.weights)) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,13,QTableWidgetItem(str(order.tape_no)) )
        self.ui.tableW_samplecheck_order.setItem(row_pos,14,QTableWidgetItem(str(order.id)) )


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
                if order.tis_no=='TIS18-SO4548':
                    logger.debug('  check this point')
                self.append_one_order(order)
        except Exception as e:
            logger.error('  error when get orders from shipment {0}'.format(e))


    def show_orders(self,orders):
        for index in range(len(orders)):
            order=orders[index]
            logger.debug('  start to show order {0}/{1}/{2}'.format(order.tis_no,order.product.style_no,order.quantity))
            try:
                self.append_one_order(order)
            except Exception as e:
                logger.error(' error occurs when show order in Table widget {0}'.format(e))

    def show_all_orders(self):
        self.ui.tableWOrder.setRowCount(0)
        orders=order_view.get_orders()
        logger.debug(' Get orders {0}'.format(len(orders)))
        #self.ui.tableWOrder.setRowCount(len(orders))
        self.show_orders(orders)


    def show_shipments(self,shipments):
        for shipment in shipments:
            logger.debug('  start to show shipment {0}'.format(shipment))
            self.append_one_shipment(shipment)

    def show_all_shipments(self,shipments):
        self.ui.tableWOrder.setRowCount(0)
        shipments=shipment_view.get_all_shipment()
        logger.debug(' Get shipments {0}'.format(len(shipments)))
        self.show_shipments(shipments)

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
        shipments=shipment_view.get_next_2month_inspection()
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
                    if size_show_l: #below get each size
                        size_no_whole=0
                        for group_no in range(len(size_show_l)):
                            size_group=size_show_l[group_no]
                            table_w=getattr(dialog.ui,'tableW_size_{0}'.format(group_no+1))
                            logger.debug('start to save data {0} to size {1} '.format(table_w,size_group))
                            for size_no in range(len(size_group)):
                                size_no_whole+=1
                                quantity=int(table_w.item(0,size_no).text())
                                setattr(order,'size{0}'.format(size_no_whole),quantity)
                    else: #new style NO. for size show,
                        logger.warn(' No this style in size show, please add to size_chart.py')

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

    def full_text_search(self):
        self.ui.tableWOrder.setRowCount(0)
        key_text=self.ui.lin_search.text()
        if not key_text:
            qm=QMessageBox()
            ret=qm.question(self,'search box','Please fill in the search text',qm.Ok)
            return
        table_l=fts_search.search_index(key_text)
        logger.debug(' Searching {0}, get {1}'.format(key_text,table_l))
        orders=[]
        shipments=[]
        for line in table_l:
            if line.get('table_name')=='orders_order':
                order=Order.objects.get(id=line.get('obj_id'))
                orders.append(order)
            elif line.get('table_name')=='shipments_shipment':
                shipment=Shipment.objects.get(id=line.get('obj_id'))
                shipments.append(shipment)
            else:
                logger.warn(' Not found this table index: {0}'.format(line.get('table_name')))
        self.show_orders(orders)
        self.show_shipments(shipments)

    def get_colour_checkbox_status(self):
        colour_checkbox_status={} #store only selected colour {'Navy':'A','Yellow':'R'}  A-Approve R-Reject
        for i in range(self.ui.tableW_colour.columnCount()): #check each check_box to get colours_selected
            try:
                colour_name = self.ui.tableW_colour.horizontalHeaderItem(i).text()
                logger.debug(' head colour name: {0}'.format(colour_name))
                colour_check_box_name='checkB_{0}'.format(colour_name)
                colour_check_box=getattr(self.ui,colour_check_box_name,False)
                logger.debug(' colour:{0} Selected={1}'.format(colour_check_box_name,colour_check_box.isChecked()))
                if colour_check_box.isChecked():
                    radioB_app=getattr(self.ui,'radioB_a_{0}'.format(colour_name))
                    logger.debug(' radioB_a_{0} selected={1}'.format(colour_name,radioB_app.isChecked()))
                    if radioB_app.isChecked():  #as 2 radio button are mutually excluded, so only need to check 1 button
                        colour_checkbox_status[colour_name]='A'
                    else:
                        colour_checkbox_status[colour_name]='R'
            except Exception as e:
                logger.error(' error {0}'.format(e))
        return colour_checkbox_status


    def check_orders(self):
        #orders=Order.objects.filter(tis_no__contains='TIS18-SO47')
        self.ui.tableW_samplecheck_order.setRowCount(0)
        supplier=self.ui.comb_supplier.currentText()
        fabric=self.ui.comb_fabric.currentText()
        colours_selected=self.get_colour_checkbox_status()
        logger.debug(' colours seleted is {0}'.format(colours_selected))
        orders=Order.objects.filter(supplier=supplier,product__fabric__nickname=fabric,\
                                    fabrictrim__colour_solid__in=colours_selected.keys(),shipment__eta__gt=datetime.date.today())
        logger.debug(' get check sample orders number: {0}'.format(len(orders)))
        for order in orders:
            self.append_samplecheck_one_order(order)
        for i in range(15): # adjust all coloum width to content
            if i in [8,9]:
                continue
            self.ui.tableW_samplecheck_order.resizeColumnToContents(i)

    def save_test_report(self):
        supplier=self.ui.comb_supplier.currentText()
        fabric=self.ui.comb_fabric.currentText()
        if not fabric:
            qm=QMessageBox()
            ret=qm.question(self,'Fabric','Please select Fabric',qm.Ok)
            return
        test_report=self.ui.lin_testreport_ref.text()
        if not test_report:
            qm=QMessageBox()
            ret=qm.question(self,'TestReport','Please fill in test report No.',qm.Ok)
            return
        comment=self.ui.lin_testreport_comment.text()
        if not comment:
            qm=QMessageBox()
            ret=qm.question(self,'TestReport','Please fill in comment',qm.Ok)
        colours_selected=self.get_colour_checkbox_status()
        orders_checked=0
        email_msg='Regarding test report {0} - {1} {2}'.format(test_report,fabric,' '.join(colours_selected.keys()))
        order_str='TIS18-SO'
        style_str=''
        comment_str=''
        for i in range(self.ui.tableW_samplecheck_order.rowCount()):
            check_box=getattr(self.ui,'checkB_samplecheck_order_{0}'.format(i))
            if not check_box.isChecked():
                continue
            try:
                order_id=int(self.ui.tableW_samplecheck_order.item(i,14).text())
                tis_no=self.ui.tableW_samplecheck_order.item(i,1).text()[-4:] #get last 4 digits after SO,
                style=self.ui.tableW_samplecheck_order.item(i,2).text()
                order_str='{0}{1} '.format(order_str,tis_no)
                style_str='{0} {1}'.format(style_str,style)
            except Exception as e:
                logger.error(' error get order_id from tableW : {0}'.format(e))
            #colour=self.ui.tableW_samplecheck_order.item(i,3).text()
            logger.debug(' start to search fabri trim for order_id {0} and colours {1}'.format(order_id,colours_selected.keys()))
            fabrictrims=FabricTrim.objects.filter(order_id=order_id,colour_solid__in=colours_selected.keys())
            logger.debug(' get fabric trims number : {0}'.format(len(fabrictrims)))
            for fabrictrim in fabrictrims:
                try:
                    testreport_check=SampleCheck(type='T',status=colours_selected.get(fabrictrim.colour_solid),comment=comment,\
                                             ref=test_report,fabric=fabrictrim,order_id=order_id,check_date=datetime.date.today())
                    testreport_check.save()
                except Exception as e:
                    logger.error(' error when saving test report: {0}'.format(e))
            logger.debug(' finish save {0} test report check for order {1}'.format(len(fabrictrims),order_id))
            orders_checked+=1
        logger.debug(' finish save test report chech for {0} orders'.format(orders_checked))
        #below assemble the msg for email
        for k,v in colours_selected.items():
            comment_str += k
            if v=='A':
                comment_str += ' approved; '
            else:
                comment_str+=' rejected; '
        comment_str+=comment
        email_msg=email_msg+' - '+order_str+' - '+style_str+'\n'+comment_str
        logger.debug(' get email_msg is:{0}'.format(email_msg))
        clipboard.write(email_msg)
        #below reset the window
        qm=QMessageBox()
        qm.question(self,'Save test report','Successfully saved test report {0} for {1} orders. Below message has been written to clipboard, you can press CTR+V to paste to your email \n {2}'.format(test_report,orders_checked,email_msg))
        self.ui.tableW_samplecheck_order.setRowCount(0)
        self.ui.lin_testreport_ref.setText('')
        self.ui.lin_testreport_comment.setText('')
        self.ui.comb_fabric.setCurrentText('--')

    def split_shipment_aw(self):
        file_name=QFileDialog.getOpenFileName(self,'Open file',os.path.join(os.path.abspath('..'),'media'))[0]
        logger.debug('start to read file {0}'.format(file_name))
        shipment_no=0
        target_l=[]
        pre_tis_no=''
        pre_style=''
        with open(file_name) as f:
            for line in f:
                if line.startswith('Container'):
                    con_no=line.split(' ')[1][0] #from Container 1: ETD: June 12th   1 X 40'HQ , get '1:' , get '1'
                    continue
                target_items=line.strip().split('\t')
                if len(target_items)<=1:
                    continue #skip blank line
                target_items.append(con_no)
                if target_items[0].startswith('SO') or target_items[0].startswith('so'):
                    pre_tis_no=target_items[0]
                    pre_style=target_items[1]
                else:
                    target_items[0]=pre_tis_no
                    target_items[1]=pre_style

                logger.debug('get line:{0}'.format(target_items))
                target_l.append(target_items)

        #below check the volume of each contianer
        import numpy as np
        try:
            target_np=np.array(target_l)
            logger.debug(' numpy array is {0}'.format(target_np))
            target_np_sliced=np.array(target_np[:,3:7],dtype=np.float)
            logger.debug(' numpy array slicing is {0}'.format(target_np_sliced))
        except Exception as e:
            logger.error(' error when conver numpy array {0}'.format(e))
        from collections import defaultdict
        volumes=defaultdict(float)
        for i in range(len(target_l)):
            volumes[target_l[i][6]]+=float(target_l[i][5])
        logger.debug(' volumes is :{0}'.format(volumes))

        #below check each order in db according to the order in email list
        for line in target_l:
            tis_no=line[0] #'SO4378'
            colour=line[2] #'C.BLUE'
            #get formal colour name and check
            colour=product_price.get_formal_colourname_from_alias(colour) #'CobaltBlue'
            if not colour:
                logger.error(' Can not find this colour alias : {0}, please add to product_price.colour_alias'.foramt(colour))
                return
            #get order in db
            try:
                order=Order.objects.get(tis_no__iendswith=tis_no,colour__iexact=colour)
            except Exception as e:
                logger.error(' error when get order for {0}/{1}: {2}'.format(tis_no,colour,e))
                return
            #check style name and quantity for this order in db comparing with email
            #check if the order is in the same origin shipment
            if order.shipment.code!=self.ui.comb_shipment_auwin_origin.currentText():
                logger.error(' the order is not in the origin shipment')
            #check if all orders in db belonging original shipment are included in email
            #update shipment


    def refresh_shipment_au_split(self):
        self.ui.comb_shipment_auwin_origin.clear()
        self.ui.listW_allshipment_au.clear()
        self.ui.listW_targetshipment_au.clear()
        shipments=Shipment.objects.filter(supplier__iexact='AUWIN',mode__iexact='Sea',etd__gt=datetime.date.today()).order_by('etd')
        logger.debug('get Auwin undeparture shipment number {0}'.format(len(shipments)))

        for shipment in shipments:
            self.ui.comb_shipment_auwin_origin.addItem(shipment.code)

    def reload_shipment_au_split(self):
        self.ui.listW_targetshipment_au.clear()
        self.ui.listW_allshipment_au.clear()
        shipments=Shipment.objects.filter(supplier__iexact='AUWIN',mode='Sea',etd__gt=datetime.date.today()).order_by('etd')
        logger.debug('get Auwin undeparture shipment number {0}'.format(len(shipments)))
        for shipment in shipments:
            self.ui.listW_allshipment_au.addItem(shipment.code)
        #below move current combox origin shipment from all_list to target_list
        current_text=self.ui.comb_shipment_auwin_origin.currentText()
        self.ui.listW_targetshipment_au.addItem(current_text)
        try:
            items=self.ui.listW_allshipment_au.findItems(current_text,Qt.MatchExactly)
            logger.debug(' find items {0}'.format(items))
            row_no = self.ui.listW_allshipment_au.row(items[0])
        except Exception as e:
            logger.error(' error find list widget : {0}'.format(e))

        self.ui.listW_allshipment_au.takeItem(row_no)

    def shipment_selected_move(self):
        if self.sender()==self.ui.toolB_move_shipment_to_target:
            target=self.ui.listW_targetshipment_au
            source=self.ui.listW_allshipment_au
        else:
            target=self.ui.listW_allshipment_au
            source=self.ui.listW_targetshipment_au
        current_text=source.currentItem().text()
        source.takeItem(source.currentRow())
        target.addItem(current_text)

    def creat_new_shipment(self):
        dialog=Dialog_New_Shipment()
        try:
            if dialog.exec_():
                dialog.save_new_shipment()
                logger.debug(' saved new shipment')
            else:
                logger.debug(' cancel save new shipment')
        except Exception as e:
            logger.error(' error {0}'.format(e))

    def load_shipment_from_supplier(self):
        self.ui.comb_shipmenttool_shipment.clear()
        supplier=self.ui.comb_shipmenttool_supplier.currentText()
        shipments=Shipment.objects.filter(supplier__iexact=supplier,instore__gt=datetime.date.today()).order_by('etd')
        logger.debug('get  un arrival shipment number {0}'.format(len(shipments)))

        for shipment in shipments:
            shipment_info='{0} / ETD:{1} / {2}'.format(shipment.code,shipment.etd,shipment.container) #AW-JUN 18-1 / ETD:12/06/2018 / 40GP
            self.ui.comb_shipmenttool_shipment.addItem(shipment_info)

    def shipment_tool_getorderinfo(self):
        shipment_code=self.ui.comb_shipmenttool_shipment.currentText().split('/')[0].strip() #AW-JUN 18-1
        if shipment_code:
            infoes=shipment_view.get_shipment_order_info(shipment_code)
        msg=''
        for info in infoes:
            msg='{0}{1}'.format(msg,info)
        clipboard.write(msg)
        qm=QMessageBox()
        qm.question(self,'Copy shipment order info','Below shipment info alread write to clipboard, you can paste to your email \n{0}'.format(msg))

    def check_shipment_booking(self):
        filename=QFileDialog.getOpenFileName(self,'Please select shipment booking spreadsheet',os.path.join(os.path.abspath('..'),'media'))[0]
        tis_app=TIS_Excel()
        try:
            #get orders in spread sheet
            l_result=tis_app.read_shipmentbooking(filename)
            orders_booking=tis_app.consolidate_order(l_result)
            logger.debug(' get booking info {0}'.format(orders_booking)) #{'TIS18-SO':{'RM123':[{'colour':},{'colour':}],'RM234':[]}}

            #get orders in db
            ship_code=self.ui.comb_shipmenttool_shipment.currentText().split('/')[0].strip()
            orders=Order.objects.filter(shipment__code__iexact=ship_code)
            l_orders_db=[]
            for order in orders:
                tis_no=order.tis_no
                colour=order.colour
                quantity=order.quantity
                cartons=order.cartons
                volume=order.volumes
                style=order.product.style_no
                order_info={'TISNo':tis_no,'Style':style,'colour':colour,'quantity':quantity,'cartons':cartons,'volume':volume}
                l_orders_db.append(order_info)
            order_db=tis_app.consolidate_order(l_orders_db)
            logger.debug(' get order from db :{0}'.format(order_db))#{'TIS18-SO':{'RM123':[{'colour':},{'colour':}],'RM234':[]}}

            #compare orders_booking with orders_db
            successful_msgs=[]
            warning_msgs=[]
            for tis_no_booking,v1_booking in orders_booking.items():
                v1_db=order_db.get(tis_no_booking)
                if not v1_db:
                    warning_msg=' Not found {0} in db '.format(tis_no_booking)
                    logger.warn(warning_msg)
                    warning_msgs.append(warning_msg)
                    continue
                for style_booking,v2_booking in v1_booking.items(): #v2=[{'colour':},{'colour'}]
                    v2_db=v1_db.get(style_booking)
                    if not v2_db:
                        warning_msg = ' Not found {0} in {1} in db'.format(style_booking,tis_no_booking)
                        logger.warn(warning_msg)
                        warning_msgs.append(warning_msg)
                        continue
                    for item_booking in v2_booking:  #item={'colour':'Navy','quantity':100,'cartons':5,'volume':0.5}
                        colour_booking=item_booking.get('colour')
                        if colour_booking=='ALL': #in booking sheet, often combine whole all order
                            quantity_db=0
                            for item_db in v2_db:
                                quantity_db+=item_db.get('quantity')
                            if quantity_db==item_booking.get('quantity'):
                                successful_msg = ' Sucessfully compare {0} {1} with quantity:{2}'.format(tis_no_booking,\
                                                                                                    style_booking,quantity_db)
                                logger.info(successful_msg)
                                successful_msgs.append(successful_msg)
                            else:
                                warning_msg = ' Quantity not same  {0} {1} with booking:{2} , db:{3}'\
                                            .format(tis_no_booking,style_booking,item_booking.get('quantity'),quantity_db)
                                logger.warn(warning_msg)
                                warning_msgs.append(warning_msg)
                            #below delete the style in relative tis_no in order_db
                            v1_db.pop(style_booking)
                            if not v1_db:
                                order_db.pop(tis_no_booking)

                        else:#Single colour, compare each
                            item_db=None
                            index=None
                            for i,e in enumerate(v2_db):
                                if e.get('colour')==colour_booking:
                                    item_db=e
                                    index=i
                            if not item_db:
                                warning_msg = ' Not found colour {0} in {1}{2} in db'. \
                                            format(colour_booking, style_booking, tis_no_booking)
                                logger.warn(warning_msg)
                                warning_msgs.append(warning_msg)
                                continue
                            #find the matched colour in db
                            quantity_db=item_db.get('quantity')
                            if quantity_db==item_booking.get('quantity'):
                                successful_msg = ' Sucessfully compare {0} {1} {2} with quantity:{3}'.format(tis_no_booking, \
                                                                                                    style_booking,colour_booking,
                                                                                                    quantity_db)
                                logger.info(successful_msg)
                                successful_msgs.append(successful_msg)
                            else:
                                warning_msg = ' Quantity not same  {0} {1} {2} with booking:{3} , db:{4}' \
                                            .format(tis_no_booking, style_booking,colour_booking, item_booking.get('quantity'),
                                                    quantity_db)
                                logger.warn(warning_msg)
                                warning_msgs.append(warning_msg)
                            #below delet the colour style in relative style,  tis_no in order_db
                            del(v2_db[index])
                            if not v2_db:
                                v1_db.pop(style_booking)
                                if not v1_db:
                                    order_db.pop(tis_no_booking)


            #check the leftover of the order_db which were not matched in order_booking
            if order_db:
                warning_msg = 'Below order in db not shown in booking'
                logger.warn(warning_msg)
                warning_msgs.append(warning_msg)

                for tis_no,v1 in order_db.items():
                    warning_msg = '  {0}-{1}'.format(tis_no,v1)
                    logger.warn(warning_msg)
                    warning_msgs.append(warning_msg)

            else:
                successful_msg = 'All order in db has been booked'
                logger.info(successful_msg)
                successful_msgs.append(successful_msg)

            warn_str='\n'.join(warning_msgs)
            successful_str='\n'.join(successful_msgs)
            email_msg=successful_str+'\n'+warn_str
            clipboard.write(email_msg)
            qm=QMessageBox()
            qm.question(self,'check booking','below checking result has copy to clipborad, you can paste to your email:{0}'.format(email_msg))


        except Exception as e:
            logger.error('error when read shipment booking {0}'.format(e))





