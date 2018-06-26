import os
import glob
from excelway.read_excel_by_xlrd import read_excel_file
from invoice import gz_packing,th_packing,st_packing,jf_packing,lt_packing
from invoice.common_validate import validate_summary,parse_invoice
from excelway.tis_excel import TIS_Excel
from TISProduction import tis_log
logger=tis_log.get_tis_logger()


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
        logger.info('- file %s has total %s sheets'%(file,len(excel_content.get('sheets'))))
        total_cartons=0
        l_msg_success=[]
        l_msg_error=[]
        l_packing_list=[]
        l_msg_recap=[]
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            if supplier in ['AW','TH','JF','ST','LT','EL']:
                validate_result,packing_list =validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db,supplier=supplier)
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
        status='There is no packing list document containing "packing" wording in file name'
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


