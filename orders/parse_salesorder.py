
import datetime
from products import size_chart
from collections import OrderedDict
import logging

def init_tissales_logger():
    f_formater=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    c_formater=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    f_handler=logging.FileHandler('tissales.log',encoding = "UTF-8")
    f_handler.setLevel(logging.DEBUG)
    f_handler.setFormatter(f_formater)

    c_handler=logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(c_formater)

    logger=logging.getLogger('tissaleslogger')
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)
    logger.setLevel(logging.DEBUG)

    return logger

def get_tissales_logger():
    return logging.getLogger('tissaleslogger')

logger=get_tissales_logger()



"""
  read from cell_list, parse each line, get a dict
  parse size from code
  order={'-RM1004':{'garment_type':'male_shirt'|'female_shirt'|'kids_shirt'|'trousers'|'femail_slacks'|'shorts',
                    'description':,
                    'price':,
                    'colour':{'-navy':{'-77R':,...},...}
                    }
        }
    target list:[doc_date,doc_no,customer_no,customer_name,style,colour,size1,size2...,size30]
    
"""

'''
assemble dictionary orders
{doc_no:{doc_date:,customer_no:,customer_name,styles:{
       style1:{'garment_type':'male_shirt',colour:{colour1:{size1:quantity1,size2:quantity2},colour2:{}},style2:{...}}}}}
'''
def read_eachline(cell_list=[], filename='', sheetname=''):
    order = {}
    nrows = len(cell_list)
    ncols = len(cell_list[0])
    logger.debug('combined cell_list is {0}-{1}'.format(nrows,cell_list))
    for rownum in range(1, nrows):
        if rownum==10:
            logger.debug('parse row {0}'.format(rownum))
            pass
        # read each cell required
        current_row = cell_list[rownum]
        code = current_row[23]
        if not code or code in ['_Code','SOC','']:
            continue
        #get comment info
        doc_date=current_row[5]
        doc_no=current_row[7]
        customer_code=current_row[17]
        customer_name=current_row[18]
        #get style info
        description = current_row[24]
        quantity = current_row[25]
        price = current_row[4]

        # parse code RM1004.Navy.C077R,
        l_code=code.split('.')
        if len(l_code)<3:
            logger.error('this code [{0}] is can not be splited completely'.format(code))
            continue
        style = code.split('.')[0]
        colour = code.split('.')[1]
        size_code = code.split('.')[2]
        size = size_chart.get_size_from_code(size_code)
        if size is None:
            logger.error('-%s-%s- can not find size code - %s' % (filename, sheetname, size_code))
        # parse description Cargo Trouser Navy 77R,
        # for 2 XL,3 XL,2 XS etc, there is space between digit and text, such as 2 Tone Open Front Shirt L/S 3MTape Orange/Navy 2 XL ,
        ele_description = description.split(' ')
        len_ele_des = len(ele_description)
        size_name = ''
        desc = ''
        if ele_description[len_ele_des - 2] in ['2', '3', '4', '5', '6', '7', '8', '9']:
            # colour=ele_description[len_ele_des-3]
            if colour in ['CobaltBlue', 'LightBlue',
                          'Fren Navy']:  # in these colour, the colour name has 2 words, like 'Colbalt Blue'
                pos = len_ele_des - 4
            else:
                pos = len_ele_des - 3
            for ele_num in range(pos):
                desc = desc + ' ' + ele_description[ele_num]

        else:
            size_name = ele_description[len_ele_des - 1]
            if style in ['RM8080', 'RM4040', 'RM2020'] and size_name.find('(') != -1:
                size_name = size[0:size.find('(')]
            # colour=ele_description[len_ele_des-2]
            if colour in ['CobaltBlue', 'LightBlue',
                          'Fren Navy']:  # in these colour, the colour name has 2 words, like 'Colbalt Blue'
                pos = len_ele_des - 3
            else:
                pos = len_ele_des - 2
            for ele_num in range(pos):
                desc = desc + ' ' + ele_description[ele_num]

        garment_type = size_chart.get_garment_type(style)
        if garment_type is None:
            logger.error('can not find this style',style)
            continue

        # assemble the order
        doc_value=order.get(doc_no)
        if doc_value is None: # for the 1st line, assemble the new doc_no
            doc_value={'doc_date':doc_date,'customer_code':customer_code,'customer_name':customer_name,'styles':{}}
        style_value = doc_value.get('styles').get(style)
        if style_value is None:  # for the 1st line, assemble the new style
            style_value = {'garment_type': garment_type,
                           'colour': {colour: {size: quantity}}}
            doc_value['styles'][style] = style_value
        else:  # for the 2nd or above line, manupulate on colour and add the size and quantity
            colour_value = style_value.get('colour')
            if colour_value.get(colour) is None:  # for new colour, assemble new colour
                colour_value[colour] = {size: quantity}
            else:
                colour_value[colour][size] = quantity
            doc_value['styles'][style]['colour'] = colour_value
        order[doc_no] = doc_value
    logger.debug('parsed order len{0} content={1}'.format(len(order.keys()),order))

    return order





"""
write to the relavant csv

"""


def save_to_csv(orders, file_path):
    size_chart = {
        'shirts': ['2XS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL', '7XL', '8XL', '9XL',
                   '10XL'],

        'male_shirt': ['2XS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL', '7XL', '8XL', '9XL',
                       '10XL'],

        'female_shirt': ['6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '-', '-', '-', '-'],

        'kids_shirt': ['Y0', 'Y1-2', 'Y3-4', 'Y5-6', 'Y7-8', 'Y9-10', 'Y11-12', 'Y13-14', '-', '-', '-', '-', '-', '-',
                       '-'],

        'male_trousers': ['67R', '72R', '77R', '82R', '87R', '92R', '97R', '102R', '107R', '112R', '117R', '122R',
                          '127R', '132R',
                          '87S', '92S', '97S', '102S', '107S', '112S', '117S', '122S', '127S', '132S', '74L', '79L',
                          '84L', '89L', '94L'],

        'trousers': ['67R', '72R', '77R', '82R', '87R', '92R', '97R', '102R', '107R', '112R', '117R', '122R', '127R',
                     '132R',
                     '87S', '92S', '97S', '102S', '107S', '112S', '117S', '122S', '127S', '132S', '74L', '79L', '84L',
                     '89L', '94L'],
        'female_slacks': ['6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '-', '-', '-', '-',
                          '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],

        'shorts': ['67', '72', '77', '82', '87', '92', '97', '102', '107', '112', '117', '122', '127', '132',
                   '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    }
    files = []
    for doc_no,doc_value in orders.items():
        general_info=[doc_value.get('doc_date'),doc_no,doc_value.get('customer_code'),doc_value.get('customer_name')]
        logger.debug('doc_no={0}, general_info={1}'.format(doc_no,general_info))
        styles=doc_value.get('styles')
        for style in styles:
            style_value = styles.get(style)
            garment_type = style_value.get('garment_type')
            if garment_type in ['male_shirt','female_shirt','kids_shirt']:
                sheet_type = 'shirts'  # all shirts in one sheet
            elif garment_type in ['male_trousers', 'female_slacks', 'shorts']:
                sheet_type = 'trousers'
            else: #skip the goverment type
                logger.error('the {0}-{1} skip'.format(garment_type,style))
                continue
            filename = file_path + '/{0:%Y} {0:%m} {0:%d} - {1}.csv'.format(datetime.date.today(), sheet_type)
            files.append(filename)
            logger.debug(' Start open file %s' % filename)
            sheet_size_title = size_chart.get(sheet_type)
            size_title = size_chart.get(garment_type)

            # if it is new file, write the title
            if not os.path.isfile(filename):
                title = ['DOC_DATE', 'DOC_NO', 'CUSTOMER_CODE', 'CUSTOMER_NAME', 'Style NO.',  'Colours',
                         'Units Ordered']
                title.extend(sheet_size_title)
                try:
                    with open(filename, 'w') as data:
                        for colnum in range(len(title) - 1):
                            print('%s,' % title[colnum], file=data, end='')
                        print(title[len(title) - 1], file=data)  # for the last column without ',' following
                except Exception as err:
                    logger.error('Can not open file %s,  error-%s' % (filename, err))
                    continue

            # assemble content
            # sorted colour
            logger.debug('style_value={0}'.format(style_value))
            colours = sorted([colour for colour in style_value.get('colour')])
            logger.debug('sorted colours is {0}'.format(colours))
            for colour in colours:
                # assembel size content and sum the qty total
                colour_value = style_value.get('colour').get(colour)
                logger.debug('start assemble colour {0},with value {1}'.format(colour, colour_value))
                size_content = []
                total_qty = 0
                for size in size_title:
                    size_value = str(colour_value.get(size,0)).replace(',','')
                    if size_value is not None:
                        size_content.append(size_value)
                        total_qty += int(float(size_value))
                    else:
                        size_content.append('')
                logger.debug('size_content is {0}'.format(size_content))

                # assemble content
                logger.debug('general_info is {0}'.format(general_info))
                content = general_info.copy()
                content.extend([style,colour,total_qty])
                content.extend(size_content)
                logger.debug('assembled content is {0}'.format(content))
                # write the content
                try:
                    with open(filename, 'a') as data:
                        for colnum in range(len(content) - 1):
                            print('%s,' % content[colnum], file=data, end='')
                        print(content[len(content) - 1], file=data)
                except Exception as err:
                    logger.error('Can not open file %s,  error-%s' % (filename, err))
                    continue

    return files



def parse_salesorder(cell_list=[],filename='',sheetname='',file_path='c:\\'):
    order=read_eachline(cell_list=cell_list,filename=filename,sheetname=sheetname)
    #logger.debug('parse sales order as below:{0}'.format(order.items()[:10]))
    #print('parse sales order as below:',order)
    result=save_to_csv(order,file_path=file_path)
    return result
        

if __name__=='__main__':
    init_tissales_logger()
    import os
    from excelway.read_excel_by_xlrd import read_excel_file
    file_path=os.path.abspath(os.path.join(os.getcwd(),'../media/sales'))
    file=os.path.join(file_path,'Original_sales_record.xlsx')
    #file=os.path.join(file_path,'test.xlsx')
    logger.debug('filename={0}'.format(file))
    excel_content = read_excel_file(file)
    if excel_content is None:
        logger.error('file empty')
        exit()
    logger.debug('Start reading file {0}, total {1} sheets'.format(file, len(excel_content.get('sheets'))))
    cell_list=[]
    for sheetname in excel_content.get('sheets'):
        logger.debug('-Start to check the sheet %s' % sheetname)
        ''' #old way is to parse every sheet in every file
        result=parse_requisiton.parse_requisition(cell_list=excel_content.get('sheets').get(sheetname),
                                            filename=excel_content.get('filename'), 
                                            sheetname=sheetname,etd_dict=etd_dict,file_path=file_path)
        '''
        # new way is combine all sheet and parse one time
        cell_list.extend(excel_content.get('sheets').get(sheetname))
    logger.debug('-Finish file')
    parse_salesorder(cell_list, filename='all_file', sheetname='all_sheet',file_path=file_path)
