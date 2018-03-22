from win32com.client import DispatchEx
from collections import OrderedDict,defaultdict
import os
from TISProduction import tis_log
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import glob
from orders import parse_requisiton
from excelway.read_excel_by_xlrd import read_excel_file


logger=tis_log.get_tis_logger()

class TIS_Excel():
    DEBUG=True
    DELAY_TIME=0
    END_STR="INDIA"
    MAX_MTM_QUANTITY=10
    ORDER_FIELD=OrderedDict([('B','Customer'),('C','Supplier'),('D','Style'),('E','TISNo'),('F','InternalNo'),('G','ShipCode'),('H','ETD'),('I','ETA'),('J','InStore'),('K','ABMInStore'),('L','CTM'),('M','Commodity'),('N','Colour'),('O','Quantity'),('P','Freight'),('Q','FOBPort'),('R','ETAPort'),('S','OrderDate'),('T','PPSample'),('U','SSSample'),('V','TestReport'),('W','Material'),('X','Cartons'),('Y','Volume'),('Z','Weight')])
    FINANCE_FIELD=OrderedDict([('A','Customer'),('B','Supplier'),('C','CTM'),('D','OrderDate'),('E','TISNo'),('F','InternalNo'),('G','Style'),('H','Commodity'),('I','Quantity'),('J','FreightPrice'),('K','ExchangeRate'),('L','LandCost'),('M','FreightCost'),('N','Sales'),('O','MarkUp'),('P','FOBPort'),('Q','Freight'),('R','ETD'),('S','ETA'),('T','InStore'),('U','FactoryPayMonth'),('V','ClientPayMonth'),('W','SellPrice'),('X','PurchasePrice'),('Y','Deposit'),('Z','FTYInvoice'),('AA','Fabric'),('AB','Colour'),('AC','Remark')])

    def __init__(self,**kwargs):
        super(TIS_Excel,self).__init__(**kwargs)
        self.excelapp=DispatchEx("Excel.Application")
        self.DisplayAlerts=False
        self.wb_order=None
        self.wb_finance=None
        if TIS_Excel.DEBUG:
            self.excelapp.Visible=True
        else:
            self.excelapp.Visible=False

    def close_wb(self):
        try:
            if self.wb_order:
                self.wb_order.Close()
        except Exception as e:
            print(e)
        try:
            if self.wb_finance:
                self.wb_finance.Close()
        except Exception as e:
            print(e)
        number_wb=self.excelapp.Workbooks.Count
        if number_wb>0:
            print('There are still {0} books opening'.format(number_wb))
            pass
        else:
            print('All books close'.format(number_wb))
            self.excelapp.Quit()
            print('excellapp has quit')

            del self.excelapp
            print('excellapp has del')

    @staticmethod
    def parse_sheet(ws,field):
        '''
        Acoording to the field, parse the used range of the ws (sheet) into a list of dict, one row is one dict
        :param ws: worksheet
        :param field: OrderdedDict, to get the filed name and excel sheet column name
        :return:  list of dict from non-modified worksheet
        '''
        ws_name='order'
        if 'ExchangeRate' in field.values():
            ws_name='finance'
        print('p-start to parse excel {0}'.format(ws_name))
        logger.debug('l-start to parse excel {0}'.format(ws_name))
        l_result=[]
        row_count=ws.UsedRange.Rows.Count
        print(row_count)
        for row_num in range(1,row_count+1):
            if (row_num % 50)==0:
                print('p-{0}'.format(row_num),end=" ")
                logger.debug('l-{0}'.format(row_num))
            d_row={}
            d_row['row_num']=row_num
            for k,v in field.items():
                cell_name='{0}{1}'.format(k,row_num)
                #value=ws.Range(cell_name).Text
                value=ws.Range(cell_name).Value
                d_row[v]=value
                #print('cell{0}: ({1}:{2})'.format(cell_name,v,value))
            #print(d_row)
            l_result.append(d_row)
        return l_result

    def read_order(self,filename="media/order.xls"):
        '''
        Iterate each row of the excel and parse to dict , append the dict to a list as return
        :param filename:
        :return: list of dict in which key is field name and value is content
        example: [{'TISNo':'TIS17-SO3111','Style':'RM1000','Colour':'Navy',...},{'TISNo':'TIS17-SO3111','Style':'RM1000','Colour':'Navy',...},{'TISNo':'TIS17-SO3112','Style':'RM1050','Colour':'Orange-Navy',...},{}...]
        '''
        try:
            self.wb_order=self.excelapp.Workbooks.open(filename)
            self.ws_order=self.wb_order.Worksheets[0]
        except Exception as e:
            print('error in open order sheets, error={0}'.format(e))
        l_order=TIS_Excel.parse_sheet(self.ws_order,TIS_Excel.ORDER_FIELD)
        return l_order

    def read_finance(self,file_name="media/finance.xls"):
        '''

        :param file_name: finance worksheet
        :return: list of dict unchanged finance sheet
        '''
        try:
            self.wb_finance=self.excelapp.Workbooks.open(file_name)
            self.ws_finance=self.wb_finance.Worksheets[0]
        except Exception as e:
            print('error in open finance sheet: {0}'.format(e))
        l_finance=TIS_Excel.parse_sheet(self.ws_finance,TIS_Excel.FINANCE_FIELD)
        logger.debug('\nFinance List is:\n{0}\n'.format(l_finance))
        return l_finance


    @staticmethod
    def consolidate_list_to_dict(orgin_list,key,is_valid):
        '''
        find the dict in the origin_list which has the same value of the para key, then consolidate to a dict with key is the distinct value and the value is a list of dict
        :param orgin_list: list of dict , example: [{'a':1,'b':2,'c':3},{'a':1,'b':3,'c':3},{'a':2,'b':2,'c':3},]
        :param key: by which key to consolidate , example: 'a'
        :return: new_dict: with key is value of the param key, value is a list of dict , example: {1:[{'b':2,'c':3},{'b':3,'c':3}],2:[{..}]}
        '''
        origin_name='order'
        if 'ExchangeRate' in orgin_list[0].keys():
            origin_name='finance'
        new_dict=defaultdict(list)
        #logger.debug('\nl-start consolidate: {0}_list with total {1}'.format(origin_name,len(orgin_list)))
        progress=0
        for item_dict in orgin_list:
            #print('consolidate origin [1]={0}'.format(item_dict.items()))
            new_key=item_dict.get(key,None)
            progress+=1
            if (progress % 50)==0:
                logger.debug('processing to -{0} for new key {1}'.format(progress, new_key))
            #logger.debug('new_key={0}'.format(new_key))
            if is_valid(new_key):
                del item_dict[key]
                new_dict[new_key].append(item_dict)
                #logger.debug('new_dict={}'.format(new_dict.get(new_key,'Faile')))
            else:
                continue
        #logger.debug('\nl-start sort: {0}_dict'.format(origin_name))
        ordered_new_dict=OrderedDict(sorted(new_dict.items(),key=lambda t:t[0]))
        return ordered_new_dict

    @staticmethod
    def is_orderno_valid(orderno):
        if orderno is not None and orderno.startswith('TIS1'):
            return True
        else:
            return False

    @staticmethod
    def is_styleno_valid(styleno):
        if styleno is None or styleno in ['Style','No.','']:
            return False
        else:
            return True

    def consolidate_order(self,origin_list):
        '''
        consolidate the order list of dict,
        step 1: consolidate by the TISNo, get a dict in which the value is list of dict.
        step 2: iterate the list, consolidate by Style
        :param origin_list: list of dict order line , get from read_order,
          example: [{'TISNo':'TIS17-SO3111','Style':'RM1000','Colour':'Navy',...},{'TISNo':'TIS17-SO3111','Style':'RM1000','Colour':'Navy',...},{'TISNo':'TIS17-SO3111','Style':'RM1050','Colour':'Orange-Navy',...},{}...],{'TISNo':'TIS17-SO3112','Style':'RM1004','Colour':'Navy',...},{}...]
        :return: { TISNo: {Style:[{},{}]}}, example: {'TIS17-SO3111',{'RM1000':[{'Colour':'Navy'},{'Colour':'Orange'}],'RM1050':[]},'TIS17-SO3112':{}}
        '''
        consol_orderno_dict=TIS_Excel.consolidate_list_to_dict(origin_list,'TISNo',TIS_Excel.is_orderno_valid)
        #print(consol_orderno_dict)
        for single_order in consol_orderno_dict:
            old_value_list=consol_orderno_dict[single_order]
            new_value_dict=TIS_Excel.consolidate_list_to_dict(old_value_list,'Style',TIS_Excel.is_styleno_valid)
            consol_orderno_dict[single_order]=new_value_dict
        return consol_orderno_dict

    def consolidate_finance(self,origin_list):
        '''
        consolidate the finance list of dict
        :param origin_list: list of dict finance line, get from read_finance
        :return:
        '''
        consol_style_dict=TIS_Excel.consolidate_list_to_dict(origin_list,'Style',TIS_Excel.is_styleno_valid)
        for single_finace in consol_style_dict:
            #logger.debug('start consolidate finance by style {0}'.format(single_finace))
            old_value_list=consol_style_dict[single_finace]
            new_value_dict=TIS_Excel.consolidate_list_to_dict(old_value_list,'TISNo',TIS_Excel.is_orderno_valid)
            consol_style_dict[single_finace]=new_value_dict
        #logger.debug('finish consolidate finance step 2 by TISNO.')
        return consol_style_dict

    @staticmethod
    def dict_to_str(dict):
        result=''
        for k,v in dict.items():
            result='{0}\n\n{1}'.format(result,k)
            for row in v:
                result='{0}\n   {1}'.format(result,row)
        return result

    @staticmethod
    def recap_order_inform(order_lines):
        '''
        calculate the quantity for the same style in one order
        :param list, order_lines: in the same order No. and style No. , there are some , colours [{'colour':,'quantity':},{}]
        :return: dict {'total-quantity':100,'colours':'Ora-Nav,Yel-Nav','row_num':128}
        '''
        total_quantity=0
        colours=""
        row_num=None
        logger.debug('start recap : {0}'.format(order_lines))
        for line in order_lines:
            quantity=line.get('Quantity')
            logger.debug('the quantity in this line is: {0}'.format(quantity))
            total_quantity+=int(line.get('Quantity'))
            colours='{0},{1}'.format(colours,line.get('Colour'))
            logger.debug('colours={0}'.format(colours))
            common_info={'row_num':'','supplier':'','order_date':'','ctm':'','etd':'','eta':'','in_store':'','internal_no':'','freight':'','fob_port':''}
            if row_num is None:
                common_info['row_num']=line.get('row_num')
                common_info['supplier']=line.get('Supplier')
                common_info['order_date']=line.get('OrderDate')
                common_info['ctm']=line.get('CTM')
                common_info['commodity']=line.get('Commodity')
                common_info['etd']=line.get('ETD')
                common_info['eta']=line.get('ETA')
                common_info['in_store']=line.get('InStore')
                common_info['internal_no']=line.get('InternalNo')
                common_info['freight']=line.get('Freight')
                common_info['fob_port']=line.get('FOBPort')
                common_info['fabric']=line.get('Material')
                common_info['ship_code']=line.get('ShipCode')
        if len(order_lines)>2:
            colours='Assorted'
        order_recap={'total_quantity':total_quantity,'colours':colours[1:]}
        order_recap.update(common_info)
        logger.debug('result={0}'.format(order_recap))
        return order_recap

    @staticmethod
    def get_pay_month(etd):
        pay_month='JAN/2018'
        month_name=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        #logger.debug('etd : {0}'.format(etd))
        etd_str=str(etd)
        #logger.debug('str(etd) : {0}'.format(etd_str))
        try:
            dt=parse(etd_str)
            logger.debug('dt={0} , type of {1}'.format(dt,type(dt)))
            dt_pay=dt+relativedelta(days=+21)
            logger.debug('pay date is 21 days after edt : {0}'.format(dt_pay))
            pay_month='{0}/{1}'.format(month_name[dt_pay.month-1],dt_pay.year)
        except Exception as e:
            logger.debug('error on parse etd {0} : {1}'.format(etd,e))
            pay_month="TBA"
        logger.debug('pay month is {0}'.format(pay_month))

        return pay_month



    def copy_order_to_finance(self,order_file=None,finance_file=None):
        '''
        copy the new order to finance sheet.
        :param order_file:
        :param finance_file:
        :return: count of rows inserted to finance sheet
        '''
        if  not order_file or order_file=="":
            order_file=os.path.join(os.path.abspath('..'),'media/order.xls')
        if not finance_file or order_file=="":
            finance_file=os.path.join(os.path.abspath('..'),'media/finance.xls')
        order_list=self.read_order(order_file)
        consol_order=self.consolidate_order(order_list)
        finance_list=self.read_finance(finance_file)
        consol_finance=self.consolidate_finance(finance_list)

        finance_last_row=self.ws_finance.UsedRange.Rows.Count
        finance_last_orderno=self.ws_finance.Range('E{0}'.format(finance_last_row)).Text
        logger.debug('The last order No. is {0}'.format(finance_last_orderno))
        print(consol_order.keys())
        try:
            lkey=list(consol_order.keys())
            index=lkey.index(finance_last_orderno)
            print('At postion of {0}'.format(index))
            new_order_list=list(consol_order.items())[index+1:] #[('TIS17-SO1234',{'RM123':[{'Colour':'Red','Quantity':30},{'Colour':'Black'}],'RM124':[]}),()]
            logger.debug(new_order_list)
            addition_row=0
            for num in range(len(new_order_list)):
                tisno=new_order_list[num][0]  #'TIS17-SO1234'
                logger.debug('\nnum={0},tisno={1}'.format(num,tisno))
                for style in new_order_list[num][1]: #style='RM123'
                    addition_row+=1
                    logger.debug('\nstyle={0}'.format(style))
                    order_recap=TIS_Excel.recap_order_inform(new_order_list[num][1].get(style))
                    #logger.debug('the total_quantity [] is {0}'.format(order_recap['total_quantity']))
                    #logger.debug('the total_quantity get is {0}'.format(order_recap.get('total_quantity')))
                    logger.debug('{0}-{1}-{2}-{3}-{4}-{5}'.format(num,tisno,style,order_recap['total_quantity'],order_recap['colours'],order_recap['row_num']))
                    mtm_flag=False
                    if order_recap['total_quantity']<=TIS_Excel.MAX_MTM_QUANTITY:
                        mtm_flag=True
                    finance_tisno_dict=consol_finance.get(style) #{'TIS17-SO1234':[{'Quantity':,'Colours':}],'TIS17-SO1235':[]}
                    found_style=False
                    found_style_factory=False
                    if finance_tisno_dict is not None: # found style in sheet
                        found_style=True
                        finance_tisno_list=list(finance_tisno_dict.items()) #[('TIS17-SO1234',[{},{}]),('TIS17-SO1235',[])]
                        logger.debug('the finance_tisno_list is {0}'.format(finance_tisno_list))
                        for finance_tisno_tup in finance_tisno_list[::-1]:#from end to begin,get max(tisno)('TIS17-SO1234',[{Quantity':,'Colours':},{}])
                            finance_non_tisno_list=finance_tisno_tup[1]#[{'Quantity':,'Colours':}], actually, only one member in list
                            logger.debug('finance_non_tisno_list is {0}'.format(finance_non_tisno_list))
                            for finance_non_tisno in finance_non_tisno_list: #{'Quantity':,'Colour':}
                                logger.debug('finance_non_tisno is {0}'.format(finance_non_tisno))
                                quantity=finance_non_tisno.get('Quantity',0)
                                #logger.debug('quantity is {0}'.format(quantity))
                                logger.debug('show quantity')
                                if (mtm_flag==(quantity<TIS_Excel.MAX_MTM_QUANTITY)) and (order_recap.get('supplier').upper()==finance_non_tisno.get('Supplier').upper()):
                                    found_style_factory=True
                                    break
                            if found_style_factory:
                                found_row_num=finance_non_tisno.get('row_num')
                                logger.debug('found_row_num is {0}'.format(found_row_num))
                                self.ws_finance.Rows('{0}'.format(found_row_num)).Copy()
                                new_row_num=addition_row+finance_last_row
                                logger.debug('start to copy from row {0} to {1}, Select {2}'.format(found_row_num,new_row_num,new_row_num))
                                self.ws_finance.Select()
                                self.ws_finance.Rows('{0}'.format(new_row_num)).Select()
                                logger.debug('start to Paste Row')
                                self.ws_finance.Paste()
                                logger.debug('start to write  #C{0} with {1}'.format(new_row_num,order_recap.get('ctm')))
                                self.ws_finance.Range('C{0}'.format(new_row_num)).Value = order_recap.get('ctm')
                                logger.debug('start to write  #D{0} with {1}'.format(new_row_num,order_recap.get('order_date')))
                                self.ws_finance.Range('D{0}'.format(new_row_num)).Value = order_recap.get('order_date')
                                logger.debug('start to write  #E{0} with {1}'.format(new_row_num,order_recap.get('tisno')))
                                self.ws_finance.Range('E{0}'.format(new_row_num)).Value=tisno
                                logger.debug('start to write  #F{0} with {1}'.format(new_row_num,order_recap.get('internal_no')))
                                self.ws_finance.Range('F{0}'.format(new_row_num)).Value = order_recap.get('internal_no')
                                if mtm_flag:
                                    logger.debug('start to write  #H{0} with {1} {2}'.format(new_row_num, order_recap.get(
                                        'commodity'), order_recap.get('ship_code')))
                                    self.ws_finance.Range('H{0}'.format(new_row_num)).Value = '{1} {2}'.format(new_row_num, order_recap.get(
                                        'commodity'), order_recap.get('ship_code'))
                                logger.debug('start to ClearComments in I{0}'.format(new_row_num))
                                self.ws_finance.Range('I{0}'.format(new_row_num)).ClearComments()
                                logger.debug('start to write  #I{0} with {1}'.format(new_row_num,order_recap.get('total_quantity')))
                                self.ws_finance.Range('I{0}'.format(new_row_num)).Value = order_recap.get('total_quantity')
                                logger.debug('start to write  #P{0} with {1}'.format(new_row_num,order_recap.get('fob_port')))
                                self.ws_finance.Range('P{0}'.format(new_row_num)).Value = order_recap.get('fob_port')
                                logger.debug('start to write  #Q{0} with {1}'.format(new_row_num,order_recap.get('freight')))
                                self.ws_finance.Range('Q{0}'.format(new_row_num)).Value = order_recap.get('freight')
                                logger.debug('start to ClearComments in R{0}'.format(new_row_num))
                                self.ws_finance.Range('R{0}'.format(new_row_num)).ClearComments()
                                logger.debug('start to write  #R{0} with {1}'.format(new_row_num,order_recap.get('etd')))
                                self.ws_finance.Range('R{0}'.format(new_row_num)).Value = order_recap.get('etd')
                                logger.debug('start to write  #S{0} with {1}'.format(new_row_num,order_recap.get('eta')))
                                self.ws_finance.Range('S{0}'.format(new_row_num)).Value = order_recap.get('eta')
                                logger.debug('start to write  #T{0} with {1}'.format(new_row_num,order_recap.get('in_store')))
                                self.ws_finance.Range('T{0}'.format(new_row_num)).Value = order_recap.get('in_store')
                                pay_month=TIS_Excel.get_pay_month(order_recap.get('etd'))
                                logger.debug('start to write  #U&V{0} with {1}'.format(new_row_num,pay_month))
                                self.ws_finance.Range('U{0}'.format(new_row_num)).Value = pay_month
                                self.ws_finance.Range('V{0}'.format(new_row_num)).Value = pay_month
                                logger.debug('start to write  #Y&Z&AC{0} with blank'.format(new_row_num))
                                self.ws_finance.Range('Y{0}'.format(new_row_num)).Value = ""
                                self.ws_finance.Range('Z{0}'.format(new_row_num)).Value = ""
                                self.ws_finance.Range('AC{0}'.format(new_row_num)).Value = ""
                                logger.debug('start to write  #AB{0} with {1}'.format(new_row_num, order_recap.get('colours')))
                                self.ws_finance.Range('AB{0}'.format(new_row_num)).Value = order_recap.get('colours')
                                break
                            else:
                                logger.info('Style {0} is a new style for supplier{1}, please raise manually'.format(style,order_recap.get('supplier')))
                    else: #no style in sheet
                        logger.info('Style {0} is a new style in finance sheet, please raise manually'.format(style))

                    if not (found_style and found_style_factory) :
                        new_row_num = addition_row + finance_last_row
                        logger.debug('Can not find this style - {0} in previous finance sheet'.format(style))
                        logger.debug('start to write  B{0} with {1}'.format(new_row_num,order_recap.get('supplier')))
                        self.ws_finance.Range('B{0}'.format(new_row_num)).Value = order_recap.get('supplier')
                        logger.debug('start to write  #C{0} with {1}'.format(new_row_num,order_recap.get('ctm')))
                        self.ws_finance.Range('C{0}'.format(new_row_num)).Value = order_recap.get('ctm')
                        logger.debug('start to write  #D{0} with {1}'.format(new_row_num,order_recap.get('order_date')))
                        self.ws_finance.Range('D{0}'.format(new_row_num)).Value = order_recap.get('order_date')
                        logger.debug('start to write  #E{0} with {1}'.format(new_row_num,order_recap.get('tisno')))
                        self.ws_finance.Range('E{0}'.format(new_row_num)).Value=tisno
                        logger.debug('start to write  #F{0} with {1}'.format(new_row_num,order_recap.get('internal_no')))
                        self.ws_finance.Range('F{0}'.format(new_row_num)).Value = order_recap.get('internal_no')
                        logger.debug('start to write  #G{0} with {1}'.format(new_row_num,style))
                        self.ws_finance.Range('G{0}'.format(new_row_num)).Value = style
                        if mtm_flag:
                            logger.debug('start to write  #H{0} with {1} {2}'.format(new_row_num, order_recap.get(
                                'commodity'), order_recap.get('ship_code')))
                            self.ws_finance.Range('H{0}'.format(new_row_num)).Value = '{1} {2}'.format(new_row_num,
                                                                                                       order_recap.get(
                                                                                                           'commodity'),
                                                                                                       order_recap.get(
                                                                                                           'ship_code'))
                        else:
                            logger.debug('start to write  #H{0} with {1}'.format(new_row_num,order_recap.get('commodity')))
                            self.ws_finance.Range('H{0}'.format(new_row_num)).Value = order_recap.get('commodity')
                        logger.debug('start to write  #I{0} with {1}'.format(new_row_num,order_recap.get('total_quantity')))
                        self.ws_finance.Range('I{0}'.format(new_row_num)).Value = order_recap.get('total_quantity')
                        logger.debug('start to write  #AA{0} with {1}'.format(new_row_num,order_recap.get('fabric')))
                        logger.debug('start to write  #P{0} with {1}'.format(new_row_num, order_recap.get('fob_port')))
                        self.ws_finance.Range('P{0}'.format(new_row_num)).Value = order_recap.get('fob_port')
                        logger.debug('start to write  #Q{0} with {1}'.format(new_row_num, order_recap.get('freight')))
                        self.ws_finance.Range('Q{0}'.format(new_row_num)).Value = order_recap.get('freight')
                        logger.debug('start to ClearComments in R{0}'.format(new_row_num))
                        self.ws_finance.Range('R{0}'.format(new_row_num)).ClearComments()
                        logger.debug('start to write  #R{0} with {1}'.format(new_row_num, order_recap.get('etd')))
                        self.ws_finance.Range('R{0}'.format(new_row_num)).Value = order_recap.get('etd')
                        logger.debug('start to write  #S{0} with {1}'.format(new_row_num, order_recap.get('eta')))
                        self.ws_finance.Range('S{0}'.format(new_row_num)).Value = order_recap.get('eta')
                        logger.debug('start to write  #T{0} with {1}'.format(new_row_num, order_recap.get('in_store')))
                        self.ws_finance.Range('T{0}'.format(new_row_num)).Value = order_recap.get('in_store')
                        pay_month = TIS_Excel.get_pay_month(order_recap.get('etd'))
                        logger.debug('start to write  #U&V{0} with {1}'.format(new_row_num, pay_month))
                        self.ws_finance.Range('U{0}'.format(new_row_num)).Value = pay_month
                        self.ws_finance.Range('V{0}'.format(new_row_num)).Value = pay_month
                        self.ws_finance.Range('AA{0}'.format(new_row_num)).Value = order_recap.get('fabric')
                        logger.debug('start to write  #AB{0} with {1}'.format(new_row_num,order_recap.get('colours')))
                        self.ws_finance.Range('AB{0}'.format(new_row_num)).Value = order_recap.get('colours')


        except Exception as e:
            logger.error('Error when finding this order, {0}'.format(e))
        try:
            self.close_wb()
        except Exception as e:
            print(e)

    def generate_product_price(self,finance_file=None):
        if finance_file =="":
            finance_file=os.path.join(os.path.abspath('..'),'media/finance.xls') #if not choose file, read from file finance_list
            #finance_list=finance_list_file.finance_list # if not choose file, read from file finance_list

        finance_list=self.read_finance(finance_file)
        consol_finance=self.consolidate_finance(finance_list)
        price_dict={}
        for style in consol_finance:
            logger.debug('\nstart to generate the price for style {0}'.format(style))
            finance_tisno_dict = consol_finance.get(style)
            finance_tisno_list = list(finance_tisno_dict.items())  # [('TIS17-SO1234',[{},{}]),('TIS17-SO1235',[])]
            sell_price=0
            purchase_price_dict={}
            for finance_tisno_tup in finance_tisno_list[::-1]:  # from end to begin,get max(tisno)('TIS17-SO1234',[{Quantity':,'Colours':},{}])
                logger.debug('finance_tisno_tup={0}'.format(finance_tisno_tup))
                finance_nontis_dict=finance_tisno_tup[1][0] #only 1 item in list[{Quantity':,'Colours':},{}]
                logger.debug('finance_nontis_dict={0}'.format(finance_nontis_dict))
                quantity=finance_nontis_dict.get('Quantity',0)
                if quantity is None:
                    quantity=0
                logger.debug('quantity={0}'.format(quantity))
                if quantity<=TIS_Excel.MAX_MTM_QUANTITY:
                    continue
                else:
                    if sell_price==0: # get the 1st price newest
                        sell_price=finance_nontis_dict.get('SellPrice',0)
                    colours_str = finance_nontis_dict.get('Colour', 'fixed')
                    if colours_str is None:
                        colours_str='fixed'
                    purchase_price=finance_nontis_dict.get('PurchasePrice',0)
                    logger.debug('sell_price={0},purchase_price={1},colours_str={2}'.format(sell_price,purchase_price,colours_str))
                    for colour in [c.strip() for c in colours_str.split(',')]:
                        if purchase_price_dict.get(colour) is None: #only get the 1st price newest
                            purchase_price_dict[colour]={'purchase_price':purchase_price,'supplier':finance_nontis_dict.get('Supplier').strip()} # \
                            #{'O-N':{'purchase_price':7.00,'factory':'Tanhoo'},'B-N':{'purchase_price':8.1,'factory':'Guangzhou'} }
                        logger.debug('finish analise colour {0} , then purchase_price_dict={1}'.format(colour,purchase_price_dict))
            price_dict[style]={'sell_price':sell_price,'purchase':purchase_price_dict}
            logger.debug('Finish style {0}, get {1}'.format(style,price_dict[style]))

        return price_dict

    @staticmethod
    def generate_from_requisition(file_path,etd_dict):
        file_position=len(file_path)+1
        files=glob.glob(file_path+'/*.xlsx')
        logger.debug('start to read requisition files in {0},total {1} files'.format(file_path,len(files)))
        for file in files:
            if file.startswith('~',file_position):
                continue
            excel_content=read_excel_file(file)
            if excel_content is None:
                continue
            logger.debug('Start reading file {0}, total {1} sheets'.format(file,len(excel_content.get('sheets'))))
            for sheetname in excel_content.get('sheets'):
                logger.debug('-Start to check the sheet %s'%sheetname)
                result=parse_requisiton.parse_requisition(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,etd_dict=etd_dict,file_path=file_path)
                if result:
                    logger.debug(result)
                    logger.debug('--Correct')
            logger.debug('-Finish file')



    def test_Excel(self,filename):
        wb=self.excelapp.WorkBooks.open(filename)
        ws=wb.Worksheets(1)
        """
        '''
        test dateutil parse date
        '''
        etd=ws.Range('H11').Value
        logger.debug('get etd form sheet {0}'.format(etd))
        result=TIS_Excel.get_pay_month(etd)
        logger.debug('pay month is {0}'.format(result))
        '''
        test copy
        '''
        '''
        test write to cell
        '''
        logger.debug('write to E10.Value')
        ws.Range('E11').Value=100
        logger.debug('write to E10.Text')
        ws.Range('E10').Value = "hello E10"
        a='finish write to E10 E11'


        '''
        test sheet UsedRange row and column count
        '''
        row_count=ws.UsedRange.Rows.Count #get excel sheet used rows count
        print('There are in UsedRange {0} rows'.format(row_count))
        column_count=ws.UsedRange.Columns.Count #get excel sheet used columns count
        print('There are in UserdRange {0} columns'.format(column_count))
        result=(row_count,column_count)
        print(result)

        '''
        test sheet count and name
        '''
        result=(wb.Worksheets.Count,ws.Name)
        a=str(result)
        '''
        test Range Value
        '''
        result=ws.Range('H4').Value
        print(type(result))
        a=str(result)
        '''
        test Range copy
        '''
        print(ws.Range('G4').Text)
        ws.Range('H4').Copy(ws.Range('G4'))
        print(ws.Range('G4').Text)
        result=ws.Range('G4').Value
        print(type(result))
        a=str(result)
        '''
        test copy range to a row
        '''
        #ws.Cells(4,1).Resize(1,26).Copy()
        ws.Range('A4:Z4').Copy()
        print(ws.Cells(row_count+1,2).Text)
        ws.Cells(row_count+1,1).Select()
        ws.Paste()
        print(ws.Cells(row_count + 1, 2).Text)
        result=ws.UsedRange.Rows.Count
        a=str(result) 
        """
        '''
        test copy whole row insert to a row
        '''
        try:
            ws.Rows('20').Insert()
            logger.debug('New row is blank - {0} - and start copy row 11'.format(ws.Cells(20,2).Text))
            ws.Rows('11').Copy()
            logger.debug('ws select')
            ws.Select()
            logger.debug("start select rows 20")
            ws.Rows('20').Select()
            logger.debug("start paste ")
            ws.Paste()
            logger.debug('start to set the TintAndShade to 0')
            ws.Rows('20').Interior.TintAndShade=0
            logger.debug('After Paste, got value - {0} -'.format(ws.Cells(20 , 2).Text))
            logger.debug("start to get the comment in I20")
            comment=ws.Range("I20").Comment
            logger.debug("the comment in I20 is {0}, start to clear comment".format(comment.Text()))
            ws.Range("I20").ClearComments()
            logger.debug("start to add the comment in I21 ")
            ws.Range("I21").AddComment("add to I121 comment")
            result=ws.UsedRange.Rows.Count
            a=str(result)
        except Exception as e:
            logger.debug("error at  {0}".format(e))
        #self.copy_order_to_finance()

        try:
            wb.Close()
            self.close_wb()
        except Exception as e:
            print('exception on:',end='')
            print(e)
        return a








