
from PyQt5.QtWidgets import QMainWindow,QFileDialog
from PyQt5.QtGui import QColor
from TISDesk.TIS_mainwindow import Ui_MainWindow
from excelway.tis_excel import TIS_Excel
from products import product_price
import os,datetime



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
        product_list=product_price.parse_product()
        product_price.init_products_db(product_list)


