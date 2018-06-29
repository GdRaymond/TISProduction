import os
import glob
from functools import reduce
from excelway.read_excel_by_xlrd import read_excel_file
from invoice import gz_packing,th_packing,st_packing,jf_packing,lt_packing
from invoice.common_validate import validate_summary,parse_invoice
from excelway.tis_excel import TIS_Excel
from TISProduction import tis_log
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
    packing_list=parse_packing_list(cell_list=cell_list,file=filename,by_name=sheetname)
    validate_result=validate_summary(packing_list=packing_list,file=filename,by_name=sheetname)
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
    if not files:
        status='There is no packing list document containing "packing" wording in file name'
        logger.warn(status)
        return({'status':status})
    for file in files:
        if file.startswith('~',len(doc_path)+1):
            continue
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
        l_msg_success=[]
        l_msg_error=[]
        l_packing_list=[]
        l_msg_recap=[]
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
                return {'status':status}

        logger.info('-Finish file, below success')
        validate_result={'status':status,'total_cartons':total_cartons,'msg_success':l_msg_success,'msg_error':l_msg_error,'msg_recap':l_msg_recap}
        #below consolidate by invoice_no, TISNo, Style
        d_packing_list_tmp=TIS_Excel.consolidate_list_to_dict(l_packing_list,'invoice_no',None) #{'AW18F206':[{},{}],'AW18F205':[]}
        d_packing_list={}
        for invoice_no,l_pk in d_packing_list_tmp.items():
            d_pk=TIS_Excel.consolidate_order(l_pk) #{'TIS17-SO4369':{'RM1050R': [{'price': 9.5, 'amount': 8189.0, 'colour': 'ALL', 'quantity': 862}]},'TIS17-SO4370':{}}
            d_packing_list[invoice_no]=d_pk
        logger.debug('after consolidate packing list d_packing_list={0}'.format(d_packing_list))

        if total_cartons:
            logger.info('--Correct, total carton={0}'.format(total_cartons))
        return validate_result,d_packing_list

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





