import os
import glob
from excelway.read_excel_by_xlrd import read_excel_file
from invoice import gz_packing,th_packing,st_packing,jf_packing,lt_packing
from invoice.common_validate import validate_summary
from invoice.th_packing import parse_packing_list as TH_parse_packing_list

from TISProduction import tis_log
logger=tis_log.get_tis_logger()


base_dir=os.path.abspath(os.path.dirname(__file__))

"""

"""
def validate_packinglist_by_sheet(cell_list=[],filename='',sheetname='',save_db=False):
    #parse_packing_list=
    packing_list=TH_parse_packing_list(cell_list=cell_list,file=filename,by_name=sheetname)
    verify_result=validate_summary(packing_list=packing_list,file=filename,by_name=sheetname)
    #if save_db==True:
        #count=save(packing_list=packing_list,fty='TH',file=filename,by_name=sheetname)
    result={'verify':verify_result,'packing_list':packing_list}

    return result


def check_shipment_document(shipment_code,doc_path,save_db=None):
    #check packing list
    logger.debug('doc_path={0}, len={1}'.format(doc_path,len(doc_path)))
    packing_path=os.path.join(doc_path,'*packing*.xls*')
    files=glob.glob(packing_path)
    logger.debug('get files={0}'.format(files))
    for file in files:
        if file.startswith('~',len(doc_path)+1):
            continue
        logger.debug('Start reading file {0}'.format(file))
        if not shipment_code:
            logger.warn('please choose shipment code first')
            return
        supplier=shipment_code.split('-')[0].lower()
        if supplier=='jf':
            excel_content=read_excel_file(file,'宁波金丰进出口有限公司')
        else:
            excel_content=read_excel_file(file)

        if excel_content is None:
            continue
        logger.info('- file%s has total %s sheets'%(file,len(excel_content.get('sheets'))))
        total_cartons=0
        l_msg_success=[]
        l_msg_error=[]
        for sheetname in sorted([each for each in excel_content.get('sheets')]):
            logger.info('-Start to check the sheet %s'%sheetname)
            if supplier=='gz':
                total_cartons+=gz_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            elif supplier=='th':
                result_th=validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
                total_cartons+=result_th.get('verify').get('total_carton')
                l_msg_success.extend(result_th.get('verify').get('msg_success'))
                l_msg_error.extend(result_th.get('verify').get('msg_error'))

            elif supplier=='st':
                total_cartons+=st_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname)
            elif supplier=='jf':
                total_cartons+=jf_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            elif supplier=='lt':
                total_cartons+=lt_packing.validate_packinglist_by_sheet(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,save_db=save_db)
            if total_cartons:
                logger.info('--Correct, total carton=')
                logger.info(total_cartons)
        logger.info('-Finish file, below success')
        result={'total_cartons':total_cartons,'msg_success':l_msg_success,'msg_error':l_msg_error}
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
    
