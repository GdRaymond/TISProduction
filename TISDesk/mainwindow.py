
from PyQt5.QtWidgets import QMainWindow,QFileDialog
from PyQt5.QtGui import QColor
from TISDesk.TIS_mainwindow import Ui_MainWindow
from excelway.tis_excel import TIS_Excel
from products import product_price
import os,datetime,time
from PyQt5.QtCore import QThread,pyqtSignal
from TISProduction import tis_log

logger=tis_log.get_tis_logger()


class WorkThread(QThread):
    signal_display=pyqtSignal(dict)

    def __init__(self,job):
        self.job=job
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
        result=excel.create_from_trace(order_file)
        self.ui.textBrowser.append('finish creating '+str(result))

    def init_products(self):
        #product_list=product_price.parse_product()
        #product_price.init_products_db(product_list)
        try:
            logger.debug('define WorkThread')
            self.work_t=WorkThread(job='init_product')
            logger.debug('connect singla')
            self.ui.textBrowser.append('connect signal')
            self.work_t.signal_display.connect(self.display)
            logger.debug('Start work_thread')
            self.ui.textBrowser.append('Start work_thread')
            self.work_t.start()
        except Exception as e:
            logger.debug(' error occur using thread {0}'.format(e))


