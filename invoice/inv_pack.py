import os,datetime
import glob,re
from functools import reduce
from excelway.read_excel_by_xlrd import read_excel_file
from invoice import gz_packing,th_packing,st_packing,jf_packing,lt_packing
from invoice.common_validate import validate_summary,parse_invoice
from excelway.tis_excel import TIS_Excel
from TISProduction import tis_log
from invoice.models import Packing,Actual_quantity
from products.size_chart import get_size_list

logger=tis_log.get_tis_logger()

class MessageList():
    def __init__(self):
        self.l_msg_error=[]
        self.l_msg_success=[]
        self.l_msg_recap=[]

    def save_msg(self,msg,type='R'):
        self.l_msg_recap.append(msg)
        if type=='E':
            self.l_msg_error.append(msg)
            logger.error(msg)
        elif type=='S':
            self.l_msg_success.append(msg)
            logger.info(msg)
        else:
            logger.info(msg)



base_dir=os.path.abspath(os.path.dirname(__file__))
PARSING_FUNC={'TH':th_packing,'AW':gz_packing,'JF':jf_packing,'ST':st_packing,'GZ':gz_packing,'EL':gz_packing}

"""

"""
def validate_packinglist_by_sheet(cell_list=[],filename='',sheetname='',save_db=False,supplier=''):
    try:
        parse_packing_list=getattr(PARSING_FUNC.get(supplier),'parse_packing_list')#dynamicly invoke parsing module according to supplier
        logger.debug('parse_packing_list={0}'.format(parse_packing_list))
        #packing_list = TH_parse_packing_list(cell_list=cell_list, file=filename, by_name=sheetname)
    except Exception as e:
        logger.error('error when invoke th parsing:{0}'.format(e))
    try:
        packing_list=parse_packing_list(cell_list=cell_list,file=filename,by_name=sheetname)
    except Exception as e:
        logger.error('error when parsing packing list : {0}'.format(e))
    logger.debug('Before validate, packing_list={0}'.format(packing_list))
    validate_result=validate_summary(packing_list=packing_list,file=filename,by_name=sheetname)
    logger.debug('After validate, packing_list={0}'.format(packing_list))
    #if save_db==True:
        #count=save(packing_list=packing_list,fty='TH',file=filename,by_name=sheetname)
    #result={'verify':verify_result,'packing_list':packing_list}

    return validate_result,packing_list


def check_shipment_packing_list(shipment_code,doc_path,save_db=None):
    status='Finished'
    #check packing list
    logger.debug('doc_path={0}, len={1}'.format(doc_path,len(doc_path)))
    packing_path=os.path.join(doc_path,'*packing*.xls*')
    files=glob.glob(packing_path)
    logger.debug('get files={0}'.format(files))

    item_no=0
    for i in range(len(files)):#because we need pop, i is only for controlling iterate times
        file=files[item_no]
        if file.startswith('~',len(doc_path)+1):
            pop_file=files.pop(item_no)
            logger.debug('iterate i={0} pop [{1}]={2}'.format(i,item_no,pop_file))
        else:
            item_no+=1 #if no pop, then do next item
    logger.debug('After pop, files={0}'.format(files))

    if not files:
        status='There is no packing list document containing "packing" wording in file name'
        logger.warn(status)
        return {'status':status},None

    l_msg_success = []
    l_msg_error = []
    l_packing_list = []
    l_msg_recap = []
    for file in files:
        logger.debug('Start reading file {0}'.format(file))
        if not shipment_code:
            logger.warn('please choose shipment code first')
            return
        supplier=shipment_code.split('-')[0]
        if supplier.lower()=='jf':
            excel_content=read_excel_file(file,'宁波金丰进出口有限公司')
        else:
            excel_content=read_excel_file(file)

        if excel_content is None:
            continue
        msg = '=============Start to verify packing list file {0} , has {1} sheets ================'.format(file,len(excel_content.get('sheets')))
        logger.info(msg)
        total_cartons=0
        l_msg_recap.append('')
        l_msg_recap.append(msg)
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            if supplier in ['AW','TH','JF','ST','LT','EL']:
                validate_result,packing_list =validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db,supplier=supplier)
                if validate_result.get('total_carton'):
                    total_cartons+=validate_result.get('total_carton')
                l_msg_success.extend(validate_result.get('msg_success'))
                l_msg_error.extend(validate_result.get('msg_error'))
                l_msg_recap.extend(validate_result.get('msg_recap'))
                l_packing_list.append(packing_list)

            else:
                status='No parsing module for this supplier {0} yet, please develop'.format(supplier)
                logger.warn(status)
                return {'status':status},None

        logger.info('-Finish file:{0}'.format(file))
    validate_result = {'status': status, 'total_cartons': total_cartons, 'msg_success': l_msg_success,
                       'msg_error': l_msg_error, 'msg_recap': l_msg_recap}
    # below consolidate by invoice_no, TISNo, Style
    d_packing_list_tmp = TIS_Excel.consolidate_list_to_dict(l_packing_list, 'invoice_no',
                                                            None)  # {'AW18F206':[{},{}],'AW18F205':[]}
    d_packing_list = {}
    for invoice_no, l_pk in d_packing_list_tmp.items():
        d_pk = TIS_Excel.consolidate_order(
            l_pk)  # {'TIS17-SO4369':{'RM1050R': [{'price': 9.5, 'amount': 8189.0, 'colour': 'ALL', 'quantity': 862}]},'TIS17-SO4370':{}}
        d_packing_list[invoice_no] = d_pk
    logger.debug('after consolidate packing list d_packing_list={0}'.format(d_packing_list))

    if total_cartons:
        logger.info('--Correct, total carton={0}'.format(total_cartons))
    return validate_result, d_packing_list



def check_shipment_invoice(shipment_code,doc_path,save_db=None):
    status='Finished'
    #check packing list
    #logger.debug('doc_path={0}, len={1}'.format(doc_path,len(doc_path)))
    packing_path=os.path.join(doc_path,'*invoice*.xls*')
    files=glob.glob(packing_path)
    #logger.debug('get files={0}'.format(files))
    if not files:
        status='There is no invoice document containing "invoice" wording in file name'
        logger.warn(status)
        return({'status':status})
    l_msg_success = []
    l_msg_error = []
    l_packing_list = []
    l_msg_recap = []
    l_invoice=[]
    for file in files:
        if file.startswith('~',len(doc_path)+1):
            continue
        #logger.debug('Start reading file {0}'.format(file))
        if not shipment_code:
            logger.warn('please choose shipment code first')
            return
        supplier=shipment_code.split('-')[0]
        excel_content=read_excel_file(file)

        if excel_content is None:
            continue
        #logger.debug('sheets={0}'.format(excel_content.get('sheets')))
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            logger.info('============{0} {1}====================='.format(file,sheetname))
            if supplier in ['AW','TH','JF','ST','LT','EL']:
                try:
                    result_validate,invoice_info =parse_invoice(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db,supplier=supplier)
                    logger.info('invoice_info={0}'.format(invoice_info))
                except Exception as e:
                    logger.error('error when parse_invoice {0} :{1}'.format(sheetname,e))
            l_msg_success.extend(result_validate.get('msg_success'))
            l_msg_error.extend(result_validate.get('msg_error'))
            l_msg_recap.extend(result_validate.get('msg_recap'))
            l_invoice.append(invoice_info)

    logger.info('-Finish file, below success')
    #consilidate the invoice list
    d_invoice=TIS_Excel.consolidate_list_to_dict(l_invoice,'invoice_no',None)
    logger.info('after consolidate, d_invoice={0}'.format(d_invoice))
    validate_result = {'status': status, 'msg_success': l_msg_success, 'msg_error': l_msg_error,
              'msg_recap': l_msg_recap}
    return validate_result,d_invoice

def check_shipment_compare_invoice_packing(shipment_code,d_invoice,d_packing_list):
    msg_list=MessageList()
    #compare invoice with packing_list
    for i_invoice_no,i_invoice_values in d_invoice.items():  # compare invoice level
        msg='' #blank line
        msg_list.save_msg(msg)
        msg='=============Start to compare invoice {0} with packing list============'.format(i_invoice_no)
        msg_list.save_msg(msg)
        p_invoice_value=d_packing_list.get(i_invoice_no)
        if not p_invoice_value:
            msg='Can not find invoice {0} in packing list'.format(i_invoice_no)
            msg_list.save_msg(msg,'E')
            continue
        for d_invoice_value in i_invoice_values: #all tisno in the list of detail #{'AWF206':[{‘total':,detail:{}}]}
            i_invoice_value=d_invoice_value.get('detail')
            for i_tisno, i_tisno_value in i_invoice_value.items():  # compare order level
                msg=''
                msg_list.save_msg(msg)
                msg = 'Start to compare order {0} in packing list'.format(i_tisno)
                msg_list.save_msg(msg)
                p_tisno_value = p_invoice_value.get(i_tisno)
                if not p_tisno_value:
                    msg = 'The order -" {0} "- shown in invoice {1} but not found in packing list'.format(i_tisno,i_invoice_no)
                    msg_list.save_msg(msg, 'E')
                    continue
                for i_style_no, i_style_value in i_tisno_value.items():  # compare style level
                    msg = '--Start to compare style {0} in packing list'.format(i_style_no)
                    msg_list.save_msg(msg)
                    p_style_value = p_tisno_value.get(i_style_no)
                    if not p_style_value:
                        msg = 'The order -" {0} {1} "- shown in invoice {2} but not found in packing list'.format(i_tisno,i_style_no, i_invoice_no)
                        msg_list.save_msg(msg, 'E')
                        continue
                    # verify price, i_style_value is a list, [{'price':9.5,'colour':'Red','Quantity':100},{}], assume price is the same
                    i_price = i_style_value[0].get('price')

                    # compare total quantity for style in invoice with packing list
                    i_total_quantity = reduce(lambda x, y: x + y,
                                              [eachcolour.get('quantity') for eachcolour in i_style_value])
                    p_total_quantity = reduce(lambda x, y: x + y,
                                              [eachcolour.get('total_quantity') for eachcolour in p_style_value])
                    if i_total_quantity == p_total_quantity:
                        msg = '--Correct total quantity {0} in both documents'.format(i_total_quantity)
                        msg_list.save_msg(msg, 'S')
                    else:
                        msg = '--Wrong total quantity invoice={0} packing list={1}'.format(i_total_quantity,
                                                                                          p_total_quantity)
                        msg_list.save_msg(msg, 'E')
                    del (p_tisno_value[i_style_no])  # after compare delete the style item in packing list
                # if all style in p_tisno_value have been delteted(compared), then delete this tisno in packing list
                if not p_tisno_value:
                    del (p_invoice_value[i_tisno])

        #if all tisno in p_invoice_value have been deleted(compared), then delete this invoice in packing list
        if not p_invoice_value:
            del(d_packing_list[i_invoice_no])
        #check if there is any item left in d_packing_list, that is the content not list in invoice
    if d_packing_list:
        for p_invoice_no,p_invoice_value in d_packing_list.items():
            for p_tisno,p_tisno_value in p_invoice_value.items():
                for p_style_no,p_style_value in p_tisno_value.items():
                    msg='The order -" {0} {1} {2} "-shown in packing list but not found in invoice'.format(p_invoice_no,p_tisno,p_style_no)
                    msg_list.save_msg(msg,'E')
    else:
        msg='All items in Packing list matched with invoice as well, nothing left'
        msg_list.save_msg(msg,'S')
    msg='Finish comparing'
    msg_list.save_msg(msg)
    validate_result={'msg_error':msg_list.l_msg_error,'msg_success':msg_list.l_msg_success,'msg_recap':msg_list.l_msg_recap}
    return validate_result

def load_packing_db_back(doc_path):
    '''
    #load invoice_packing
    file_name=os.path.join(doc_path,'packings.csv')
    logger.info('Start to load packing from file: '.format(file_name))
    with open(file_name) as f:
        for i,line in enumerate(f):
            if i==0: #skip title row
                continue
            logger.info('row={0},value={1}'.format(i,line))
            packing_l=line.split('|')
            if packing_l[12]:
                invoice_date=datetime.datetime.strptime(packing_l[12], '%Y-%m-%d')
            else:
                invoice_date=None
            packing_d={'id':int(packing_l[0]),'tis_no':packing_l[1],'internal_no':packing_l[2],'supplier':packing_l[3]\
                ,'style':packing_l[4],'commodity':packing_l[5],'price':float(packing_l[6]),'invoice_no':packing_l[7]\
                ,'total_quantity':int(packing_l[8]),'total_carton':int(packing_l[9]),'total_weight':float(packing_l[10])\
                ,'total_volume':float(packing_l[11]),'invoice_date':invoice_date\
                ,'source':packing_l[13]}
            logger.info('packing_d={0}'.format(packing_d))
            try:
                Packing.objects.create(**packing_d)
            except Exception as e:
                logger.error('error when save packing row{0}: {1}'.format(i,e))

    #load invoice_packing
    file_name=os.path.join(doc_path,'actual_qty.csv')
    logger.info('Start to load actual quantity from file: '.format(file_name))
    with open(file_name) as f:
        for i,line in enumerate(f):
            if i==0: #skip title row
                continue
            logger.info('row={0},value={1}'.format(i,line))
            actual_l=line.split('|')
            actual_d={'id':int(actual_l[0]),'packing_id':int(actual_l[1]),'colour':actual_l[2],'total_quantity':int(actual_l[3])\
                ,'size1':int(actual_l[4]),'size2':int(actual_l[5]),'size3':int(actual_l[6]),'size4':int(actual_l[7])\
                ,'size5':int(actual_l[8]),'size6':int(actual_l[9]),'size7':int(actual_l[10]),'size8':int(actual_l[11])\
                ,'size9':int(actual_l[12]),'size10':int(actual_l[13]),'size11':int(actual_l[14]),'size12':int(actual_l[15])\
                ,'size13':int(actual_l[16]),'size14':int(actual_l[17]),'size15':int(actual_l[18]),'size16':int(actual_l[19])\
                ,'size17':int(actual_l[20]),'size18':int(actual_l[21]),'size19':int(actual_l[22]),'size20':int(actual_l[23])\
                ,'size21':int(actual_l[24]),'size22':int(actual_l[25]),'size23':int(actual_l[26]),'size24':int(actual_l[27])\
                ,'size25':int(actual_l[28]),'size26':int(actual_l[29]),'size27':int(actual_l[30]),'size28':int(actual_l[31])\
                ,'size29':int(actual_l[32]),'size30':int(actual_l[33])}
            logger.info('actual_d={0}'.format(actual_d))
            try:
                Actual_quantity.objects.create(**actual_d)
            except Exception as e:
                logger.error('error when save Actual_quantity row{0}: {1}'.format(i,e))
    '''
    #load invoice_packing
    file_name=os.path.join(doc_path,'actual_qty.csv')
    logger.info('Start to load actual quantity from file: '.format(file_name))
    with open(file_name) as f:
        for i,line in enumerate(f):
            if i==0: #skip title row
                continue
            logger.info('row={0},value={1}'.format(i,line))
            actual_l=line.split('|')
            actual_d={'id':int(actual_l[0]),'packing_id':int(actual_l[1]),'colour':actual_l[2],'total_quantity':int(actual_l[3])\
                ,'size1':int(actual_l[4]),'size2':int(actual_l[5]),'size3':int(actual_l[6]),'size4':int(actual_l[7])\
                ,'size5':int(actual_l[8]),'size6':int(actual_l[9]),'size7':int(actual_l[10]),'size8':int(actual_l[11])\
                ,'size9':int(actual_l[12]),'size10':int(actual_l[13]),'size11':int(actual_l[14]),'size12':int(actual_l[15])\
                ,'size13':int(actual_l[16]),'size14':int(actual_l[17]),'size15':int(actual_l[18]),'size16':int(actual_l[19])\
                ,'size17':int(actual_l[20]),'size18':int(actual_l[21]),'size19':int(actual_l[22]),'size20':int(actual_l[23])\
                ,'size21':int(actual_l[24]),'size22':int(actual_l[25]),'size23':int(actual_l[26]),'size24':int(actual_l[27])\
                ,'size25':int(actual_l[28]),'size26':int(actual_l[29]),'size27':int(actual_l[30]),'size28':int(actual_l[31])\
                ,'size29':int(actual_l[32]),'size30':int(actual_l[33])}
            logger.info('actual_d={0}'.format(actual_d))
            try:
                Actual_quantity.objects.create(**actual_d)
            except Exception as e:
                logger.error('error when save Actual_quantity row{0}: {1}'.format(i,e))

'''
There are different type of invoice date in packing list from different supplier
'''
def parse_date(s):
    if s is None:
        logger.info(' not found date info in packing sheet')
        return None
    if type(s) is datetime.date or type(s) is datetime.datetime:
        return s
    if type(s) is str:
        match=re.match(r'([a-zA-Z]+)\s*(\d+)\s*[,.]?(\d+)',s)
        if match is not None:
            month_dict={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            month=month_dict.get(match.group(1).strip().upper()[0:3])
            day=int(match.group(2))
            year=int(match.group(3))
            if year<100:
                year=2000+year
            result=datetime.date(year,month,day)
            logger.debug('-get the invoice date is %s'%result)
            return result

        match=re.match(r'(\d+)\s*([a-zA-Z]+)\s*[,.]?(\d+)',s)
        if match is not None:
            month_dict={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            month=month_dict.get(match.group(2).strip().upper()[0:3])
            day=int(match.group(1))
            year=int(match.group(3))
            if year<100:
                year=2000+year
            result=datetime.date(year,month,day)
            logger.debug('-get the invoice date is %s'%result)
            return result

        match=re.match(r'(\d{4})\s*[,.-]\s*(\d+)\s*[,.-]\s*(\d+)',s)  #yyyy.mm.dd
        if match is not None:
            month=int(match.group(2))
            day=int(match.group(3))
            year=int(match.group(1))
            if year<100:
                year=2000+year
            logger.debug('-get the invoice date yyyy-%s,mm-%s,dd-%s'%(year,month,day))
            result=datetime.date(year,month,day)
            logger.debug('-get the invoice date is %s'%result)
            return result

        match=re.match(r'(\d+)\s*[,.-]\s*(\d+)\s*[,.-]\s*(\d{4})',s)  #dd.mm.yyyy
        if match is not None:
            month=int(match.group(2))
            day=int(match.group(1))
            year=int(match.group(3))
            if year<100:
                year=2000+year
            logger.debug('-get the invoice date yyyy-%s,mm-%s,dd-%s'%(year,month,day))
            result=datetime.date(year,month,day)
            logger.debug('-get the invoice date is %s'%result)
            return result

        match=re.match(r'(\d+)\s*[,.-]\s*(\d+)\s*[,.-]\s*(\d{2})',s)  #dd.mm.yy
        if match is not None:
            month=int(match.group(2))
            day=int(match.group(1))
            year=int(match.group(3))
            if year<100:
                year=2000+year
            logger.debug('-get the invoice date yyyy-%s,mm-%s,dd-%s'%(year,month,day))
            result=datetime.date(year,month,day)
            logger.debug('-get the invoice date is %s'%result)
            return result

        logger.error('- can not match format May 20,2012 or 20 May,2012 or 2012.5.20 or 2012-5-20')
        return None
    logger.error(' - the type of parameter-s is %s,can not parse'%type(s))
    return None

def save_packing_list(d_packing_list,supplier):
    msg_list=MessageList()
    if not d_packing_list:
        return
    msg='Start to save bundles of packing lists'
    msg_list.save_msg(msg)
    #logger.info('{0}'.format(d_packing_list))
    for invoice,in_value in d_packing_list.items(): #'AW17F204L': OrderedDict([('TIS16-SO3576',
        logger.info('')
        msg='===Invoice No.= {0}'.format(invoice)
        msg_list.save_msg(msg)
        for tis_no,tis_value in in_value.items(): #'TIS16-SO3576', OrderedDict([('RMPC014',
            msg='****TIS_NO={0}'.format(tis_no)
            msg_list.save_msg(msg)
            for style,sty_value in tis_value.items(): #'RMPC014':[{'total_volume': 6.6144,'total_quantity': 2155.0,'date': datetime.datetime(2017, 4, 25, 0, 0), 'summary': {
                msg='------Style={0}'.format(style)
                msg_list.save_msg(msg)
                size_list = get_size_list(style)
                if not size_list:
                    msg='!!!!!!!Can not find size list for style {0}'.format(style)
                    msg_list.save_msg(msg,'E')
                    continue

                for d_style in sty_value: #style_value is a list, d_style={'total_volume': 6.6144,'total_quantity': 2155.0,'date': datetime.datetime(2017, 4, 25, 0, 0), 'summary': {
                    invoice_date=d_style.get('date')
                    if invoice_date:
                        invoice_date=parse_date(invoice_date)
                    else:
                        msg='!!!!!!!! no invoice date for style: {0}'.format(style)
                        msg_list.save_msg(msg,'E')
                    commodity=d_style.get('style_description')
                    total_quantity=d_style.get('total_quantity')
                    if total_quantity:
                        try:
                            total_quantity=int(float(total_quantity))
                        except Exception as e:
                            msg='error when convert total_quantity:{0} to int: {1}'.format(total_quantity,e)
                            msg_list.save_msg(msg,'E')
                            total_quantity=0
                    total_carton=d_style.get('total_carton')
                    if total_carton:
                        try:
                            total_carton=int(float(total_carton))
                        except Exception as e:
                            logger.error('!!!!!!!!!! error when convert total_carton  {0} to interger : {1}'.format(total_carton,e))
                            total_carton=0
                    total_volume=d_style.get('total_volume')
                    total_gw=d_style.get('total_gw')

                    logger.info('........Total_quantity={0},invoice_date={1},description={2}'.format(total_quantity,invoice_date,commodity))
                    #below save Packing
                    packing_d = {'tis_no': tis_no, 'supplier': supplier, 'style': style, 'commodity': commodity\
                        ,'invoice_no': invoice, 'total_quantity': total_quantity, 'total_carton': total_carton\
                        ,'total_weight': total_gw , 'total_volume': total_volume, 'invoice_date': invoice_date }
                    msg='       total_quantity={0} invoice_date={1}'.format(packing_d.get('total_quantity'),packing_d.get('invoice_date'))
                    msg_list.save_msg(msg)
                    try:
                        packing=Packing.objects.create(**packing_d)
                        msg='       saved to db'
                        msg_list.save_msg(msg)
                    except Exception as e:
                        msg='error when save packing : {0}'.format(e)
                        msg_list.save_msg(msg,'E')
                        continue

                    d_summary=d_style.get('summary') #'summary': {'BLACK': {Actual Qty': {
                    for colour,colo_value in d_summary.items():
                        d_actual_qty=colo_value.get('Actual Qty')# {Actual Qty': {'size_qty': {'102R': 60.0, '92R': 100.0, '82R':...}'total': 1076.0},
                        colour_total_quantity=d_actual_qty.get('total')
                        msg='        colour={0}, quantity={1}'.format(colour,colour_total_quantity)
                        msg_list.save_msg(msg)
                        actual_d = {'packing_id': packing.id, 'colour': colour,'total_quantity':colour_total_quantity}
                        #actual_d = {'packing_id': 1, 'colour': colour,'total_quantity':colour_total_quantity}
                        size_quantity=d_actual_qty.get('size_qty')
                        for size_no in range(len(size_list)):
                            size_name=size_list[size_no]
                            quantity=size_quantity.get(size_name)
                            if not quantity:
                                logger.info('         packing list does no contain size {0}'.format(size_name))
                                continue
                            try:
                                quantity=int(float(quantity))
                            except Exception as e:
                                logger.error('error when coverting size {0} quantity : {1}'.format(size_name,e))
                                continue
                            logger.info('         size{0} / {1} = {2} pcs'.format(size_no+1,size_name,quantity))
                            actual_d['size{0}'.format(size_no+1)]=quantity
                        #below save actual
                        msg='         actual_d={0}'.format(actual_d)
                        msg_list.save_msg(msg)
                        try:
                            Actual_quantity.objects.create(**actual_d)
                            msg='         saved to db'
                            msg_list.save_msg(msg)
                        except Exception as e:
                            msg='error when save Actual_quantity row{0}'.format(e)
                            msg_list.save_msg(msg,'E')
    msg = 'Finish saving'
    msg_list.save_msg(msg)
    validate_result = {'msg_error': msg_list.l_msg_error, 'msg_success': msg_list.l_msg_success,
                       'msg_recap': msg_list.l_msg_recap}
    return validate_result







