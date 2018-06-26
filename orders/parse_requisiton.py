import os
import re
import xdrlib,sys
import xlrd
from excelway.read_excel_by_xlrd import  excel_read_everycell
from TISProduction import tis_log
import datetime
from products import size_chart,product_price


"""
The diction of packing_lis is as below:
{'detail':[{'form':,'to:','carton_qty':,'colour_detail':,'per_carton_pcs':,'per_carton_gw':,'per_carton_nw':,
            'subtotal':,'length':,'width':,'height':,'size_qty':{-xs:, ...}}],
 'summary':{-COBALT BLUE:{'Order Qty':{'total':, 'size_qty':{-xs:,....}},
                          'Actual Qty':{'total':, 'size_qty':{-xs:,....}},
                          'Balance':{'total':, 'size_qty':{-xs:,....}},
                          'Ratio':{'total':, 'size_qty':{-xs:,....}}
                          }
                          ...
            }
 'total_quantity':,'total_carton':,'total_gw':,'total_nw':,'total_volume':,'style_no':,'style_description':,
 'invoice_no':,'date':,'order_no':
}
"""

logger=tis_log.get_tis_logger()

"""
  read from cell_list, parse each line, get a dict
  parse size from code
  order={'-RM1004':{'garment_type':'male_shirt'|'female_shirt'|'kids_shirt'|'trousers'|'femail_slacks'|'shorts',
                    'description':,
                    'price':,
                    'colour':{'-navy':{'-77R':,...},...}
                    }
        }
"""


def read_eachline(cell_list=[], filename='', sheetname=''):
    order = {}
    nrows = len(cell_list)
    ncols = len(cell_list[0])
    for rownum in range(1, nrows):
        if rownum==10:
            logger.debug('parse row {0}'.format(rownum))
            pass
        # read each cell required
        current_row = cell_list[rownum]
        code = current_row[0]
        if not code:
            continue #2018-06-26 upgrade to get requisition wholly, there will be blank line
        description = current_row[1]
        quantity = current_row[3]
        price = current_row[4]

        # parse code RM1004.Navy.C077R,
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
            logger.error('can not find this style')
            continue

        # assemble the order
        style_value = order.get(style)
        if style_value is None:  # for the 1st line, assemble the new style
            style_value = {'garment_type': garment_type, 'description': desc, 'price': price,
                           'colour': {colour: {size: quantity}}}
            order[style] = style_value
        else:  # for the 2nd or above line, manupulate on colour and add the size and quantity
            colour_value = style_value.get('colour')
            if colour_value.get(colour) is None:  # for new colour, assemble new colour
                colour_value[colour] = {size: quantity}
            else:
                colour_value[colour][size] = quantity
            style_value['colour'] = colour_value
        order[style] = style_value
    logger.debug('parsed order:{0}'.format(order))

    return order


"""
parse file name and return the genenral info
general_info={'supplier':,'ship_mon','freight_way','etd_date','eta_date','del_date','order_date'}
"""
def get_general_info(style,colour,etd_dict=None):
    tt_day={'TANHOO':30,'AUWIN':13,'JIN FENG':11,'SMARTEX':30,'ELIEL':11,'GUANGZHOU':13,'SHANGYU':11}
    default_product_price=product_price.product_price.get(style,None)
    logger.debug('default_product_price is {0}'.format(default_product_price))
    if default_product_price is None:
        return {'factory':'','ship_mon':'','freight_way':'','etd_date':'','eta_date':'','del_date':'','order_date':''}
    default_colour=default_product_price.get('purchase').get(colour)
    logger.debug('1st default_colour is {0}'.format(default_colour))
    if default_colour is None:
        default_colour=default_product_price.get('purchase').get('Assorted')
        logger.debug('2nd default_colour is {0}'.format(default_colour))
        if default_colour is None:
            return {'factory': '', 'ship_mon': '', 'freight_way': '', 'etd_date': '', 'eta_date': '', 'del_date': '',
                    'order_date': ''}
    supplier=default_colour.get('supplier').upper()
    #elements=filename.split('-')
    #logger.debug('file name split into%s'%elements)
    general_info={}
    general_info['freight_way']='Sea'
    general_info['supplier']=supplier
    try:
        etd_date=etd_dict.get(supplier,datetime.datetime.now())
        logger.debug('etd date: {0}'.format(etd_date))
    except Exception as e:
        logger.error(' Can not get the etd factory %s error-%s' %(supplier,e))
        return None
    eta_date=etd_date+datetime.timedelta(days=tt_day[general_info['supplier']])
    del_date=eta_date+datetime.timedelta(days=3)
    mon=etd_date.strftime("%B").upper()[0:3]
    general_info['ship_mon']="'"+mon+'/'+etd_date.strftime("%Y")
    general_info['etd_date']=etd_date.strftime("%d/%m/%Y")
    general_info['eta_date']=eta_date.strftime("%d/%m/%Y")
    general_info['del_date']=del_date.strftime("%d/%m/%Y")
    general_info['order_date']=datetime.date.today().strftime("%d/%m/%Y")

    return general_info

"""
write to the relavant csv

"""
def save_to_csv(order_qty,etd_dict,file_path):
    size_chart={
        'shirts': ['2XS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL', '7XL', '8XL', '9XL',
                       '10XL'],

        'male_shirt':['2XS','XS','S','M','L','XL','2XL','3XL','4XL','5XL','6XL','7XL','8XL','9XL','10XL'],
        
        'female_shirt':['6','8','10','12','14','16','18','20','22','24','26','-','-','-','-'],
        
        'kids_shirt':['Y0','Y1-2','Y3-4','Y5-6','Y7-8','Y9-10','Y11-12','Y13-14','-','-','-','-','-','-','-'],
        
        'male_trousers':['67R','72R','77R','82R','87R','92R','97R','102R','107R','112R','117R','122R','127R','132R',
                    '87S','92S','97S','102S','107S','112S','117S','122S','127S','132S','74L','79L','84L','89L','94L'],
        
        'trousers':['67R','72R','77R','82R','87R','92R','97R','102R','107R','112R','117R','122R','127R','132R',
                    '87S','92S','97S','102S','107S','112S','117S','122S','127S','132S','74L','79L','84L','89L','94L'],
        'female_slacks':['6','8','10','12','14','16','18','20','22','24','-','-','-','-',
                    '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-'],

        'shorts':['67','72','77','82','87','92','97','102','107','112','117','122','127','132',
                    '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-']
        }
    files=[]
    for style in order_qty:
        style_value=order_qty.get(style)
        garment_type=style_value.get('garment_type')
        description=style_value.get('description').replace(',',' ') #as target is .csv, the ',' need to be replace
        sheet_type='shirts' #all shirts in one sheet
        if garment_type in ['male_trousers','female_slacks','shorts']:
            sheet_type='trousers'
        filename=file_path+'/{0:%Y} {0:%m} {0:%d} - {1}.csv'.format(datetime.date.today(),sheet_type)
        files.append(filename)
        logger.debug(' Start open file %s'%filename)
        sheet_size_title=size_chart.get(sheet_type)
        size_title=size_chart.get(garment_type)

        #if it is new file, write the title
        if not os.path.isfile(filename):
            title=['TIS O/N','ABM Internal O/N','ST','FTY','Ship MON','Style NO.','Commodity','Colours','Units Ordered']
            title.extend(sheet_size_title)
            title.extend(['Freight Way','Shipment Date','ETA Date','Del to Ritemate Warehouse','order & inform to factory','Invoice Ref No.'])
            try:
                with open(filename,'w') as data:
                    for colnum in range(len(title)-1):
                        print('%s,'%title[colnum],file=data,end='')
                    print(title[len(title)-1],file=data) #for the last column without ',' following
            except Exception as err:
                logger.error('Can not open file %s,  error-%s'%(filename,err))
                continue

        #assemble content
        #sorted colour
        logger.debug('style_value={0}'.format(style_value))
        colours=sorted([colour for colour in  style_value.get('colour')])
        logger.debug('sorted colours is {0}'.format(colours))
        for colour in colours:            
            #assembel size content and sum the qty total
            colour_value=style_value.get('colour').get(colour)
            logger.debug('start assemble colour {0},with value {1}'.format(colour,colour_value))
            size_content=[]
            total_qty=0
            for size in size_title:
                size_value=colour_value.get(size)
                if size_value is not None:
                    size_content.append(size_value)
                    total_qty+=int(float(size_value))
                else:
                    size_content.append('')
            logger.debug('size_content is {0}'.format(size_content))
            
            """
            parse file name and return the genenral info
            general_info={'fty':,'ship_mon','freight_way','etd_date','eta_date',del_date',order_date'}
            """
            #assemble content
            general_info=get_general_info(style,colour,etd_dict)
            logger.debug('general_info is {0}'.format(general_info))
            content=['','','',general_info.get('supplier'),general_info.get('ship_mon'),style,description,colour,total_qty]
            content.extend(size_content)
            content.extend([general_info.get('freight_way'),general_info.get('etd_date'),general_info.get('eta_date')
                            ,general_info.get('del_date'),general_info.get('order_date'),''])
            logger.debug('assembled content is {0}'.format(content))
            #write the content
            try:
                with open(filename,'a') as data:
                    for colnum in range(len(content)-1):
                        print('%s,'%content[colnum],file=data,end='')
                    print(content[len(content)-1],file=data)
            except Exception as err:
                logger.error('Can not open file %s,  error-%s'%(filename,err))
                continue
    return files        

"""

"""
def parse_requisition(cell_list=[],filename='',sheetname='',etd_dict={},file_path=''):
    order=read_eachline(cell_list=cell_list,filename=filename,sheetname=sheetname)
    result=save_to_csv(order,etd_dict,file_path=file_path)
    return result
        

    
