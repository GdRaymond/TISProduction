import os
import glob
from excelway.read_excel_by_xlrd import read_excel_file
from invoice import gz_packing,th_packing,st_packing,jf_packing,lt_packing
from invoice.common_validate import validate_summary
from invoice.th_packing import parse_packing_list as TH_parse_packing_list

from TISProduction import tis_log
logger=tis_log.get_tis_logger()


base_dir=os.path.abspath(os.path.dirname(__file__))
PARSING_FUNC={'TH':th_packing,'AW':gz_packing,'JF':jf_packing,'ST':st_packing,'GZ':gz_packing,'EL':gz_packing}

"""

"""
def validate_packinglist_by_sheet(cell_list=[],filename='',sheetname='',save_db=False,supplier=''):
    try:
        parse_packing_list=getattr(PARSING_FUNC.get(supplier),'parse_packing_list')
        logger.debug('parse_packing_list={0}'.format(parse_packing_list))
        #packing_list = TH_parse_packing_list(cell_list=cell_list, file=filename, by_name=sheetname)
    except Exception as e:
        logger.error('error when invoke th parsing:{0}'.format(e))
    packing_list=parse_packing_list(cell_list=cell_list,file=filename,by_name=sheetname)
    verify_result=validate_summary(packing_list=packing_list,file=filename,by_name=sheetname)
    #if save_db==True:
        #count=save(packing_list=packing_list,fty='TH',file=filename,by_name=sheetname)
    result={'verify':verify_result,'packing_list':packing_list}

    return result


def check_shipment_document(shipment_code,doc_path,save_db=None):
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
        if supplier=='jf':
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
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            if supplier in ['AW','TH','JF','ST','LT','EL']:
                result_validate =validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db,supplier=supplier)
                total_cartons+=result_validate.get('verify').get('total_carton')
                l_msg_success.extend(result_validate.get('verify').get('msg_success'))
                l_msg_error.extend(result_validate.get('verify').get('msg_error'))
                l_packing_list.append(result_validate.get('packing_list'))

            else:
                status='No parsing module for this supplier {0} yet, please develop'.format(supplier)
                logger.warn(status)
                return {'status':status}

            if total_cartons:
                logger.info('--Correct, total carton=')
                logger.info(total_cartons)
        logger.info('-Finish file, below success')
        result={'status':status,'total_cartons':total_cartons,'msg_success':l_msg_success,'msg_error':l_msg_error}
        return result




#def validate_packing_list_gz(path='gz'):
def check_packinglist(path='th',save_db=False):
    data_path=os.path.join(base_dir,path)
    logger.info('Data_path=%s, len=%s'%(data_path,len(data_path)))
    file_position=len(data_path)+1 #including the char \
    data_path=os.path.join(data_path,"*.xls*")
    logger.debug('data files path=%s'%data_path)
    files=glob.glob(data_path)
    logger.info('Total %s files'%len(files))
    
    for file in files:
        logger.info('Start reading file%s'%(file))
        if file.startswith('~',file_position):
            continue
        if path=='jf':
            excel_content=read_excel_file(file,'宁波金丰进出口有限公司')
        else:
            excel_content=read_excel_file(file)

        if excel_content is None:
            continue
        logger.info('- file%s has total %s sheets'%(file,len(excel_content.get('sheets'))))
        result=0
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            if path=='gz':
                result+=gz_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            elif path=='th':
                result+=th_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            elif path=='st':
                result+=st_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname)
            elif path=='jf':
                result+=jf_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            elif path=='lt':
                result+=lt_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            if result:
                logger.info('--Correct, total carton=')
                logger.info(result)
        logger.info('-Finish file')
    
