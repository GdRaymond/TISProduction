import os
import re
import xdrlib,sys
import xlrd
from excelway.read_excel_by_xlrd import  excel_read_everycell
from TISProduction import tis_log
import datetime
from products import size_chart,product_price,models
from collections import OrderedDict

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
    logger.debug('combined cell_list is {0}-{1}'.format(nrows,cell_list))
    for rownum in range(1, nrows):
        if rownum==10:
            logger.debug('parse row {0}'.format(rownum))
            pass
        # read each cell required
        current_row = cell_list[rownum]
        code = current_row[0]
        if not code or code=='Code':
            continue #2018-06-26 upgrade to get requisition wholly, there will be blank line, 2018-11-15 upgrade to get all requsitons , so there will be more title
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

        #get fabric content for sorted purpose
        fabric=models.Fabric.objects.get(product__style_no__iexact=style)
        if not fabric:
            fabric_nickname='Unknown'
            fabric_content='Unknown'
        else:
            fabric_nickname = 'f-{0}'.format(fabric.nickname)
            fabric_content='{0}'.format(fabric.fabric)

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
        style_value['fabric']=fabric_nickname
        style_value['fabric_content']=fabric_content
        order[style] = style_value
    logger.debug('parsed order:{0}'.format(order))

    return order


"""
parse file name and return the genenral info
general_info={'supplier':,'ship_mon','freight_way','etd_date','eta_date','del_date','order_date'}
"""
def get_general_info(style,colour,etd_dict=None):
    tt_day={'TANHOO':35,'AUWIN':13,'JIN FENG':11,'SMARTEX':35,'ELIEL':11,'GUANGZHOU':13,'SHANGYU':11}
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
    eta_date=etd_date+datetime.timedelta(days=tt_day.get(general_info['supplier'],0))
    #eta_date=etd_date
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
"""

def save_to_csv(order_qty, etd_dict, file_path):
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
    for style in order_qty:
        style_value = order_qty.get(style)
        garment_type = style_value.get('garment_type')
        description = style_value.get('description').replace(',', ' ')  # as target is .csv, the ',' need to be replace
        sheet_type = 'shirts'  # all shirts in one sheet
        if garment_type in ['male_trousers', 'female_slacks', 'shorts']:
            sheet_type = 'trousers'
        filename = file_path + '/{0:%Y} {0:%m} {0:%d} - {1}.csv'.format(datetime.date.today(), sheet_type)
        files.append(filename)
        logger.debug(' Start open file %s' % filename)
        sheet_size_title = size_chart.get(sheet_type)
        size_title = size_chart.get(garment_type)

        # if it is new file, write the title
        if not os.path.isfile(filename):
            title = ['TIS O/N', 'ABM Internal O/N', 'ST', 'FTY', 'Ship MON', 'Style NO.', 'Commodity', 'Colours',
                     'Units Ordered']
            title.extend(sheet_size_title)
            title.extend(
                ['Freight Way', 'Shipment Date', 'ETA Date', 'Del to Ritemate Warehouse', 'order & inform to factory',
                 'Invoice Ref No.'])
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
                size_value = colour_value.get(size)
                if size_value is not None:
                    size_content.append(size_value)
                    total_qty += int(float(size_value))
                else:
                    size_content.append('')
            logger.debug('size_content is {0}'.format(size_content))

            '''
            parse file name and return the genenral info
            general_info={'fty':,'ship_mon','freight_way','etd_date','eta_date',del_date',order_date'}
            '''
            # assemble content
            general_info = get_general_info(style, colour, etd_dict)
            logger.debug('general_info is {0}'.format(general_info))
            content = ['', '', '', general_info.get('supplier'), general_info.get('ship_mon'), style, description,
                       colour, total_qty]
            content.extend(size_content)
            content.extend([general_info.get('freight_way'), general_info.get('etd_date'), general_info.get('eta_date')
                               , general_info.get('del_date'), general_info.get('order_date'), ''])
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
"""

"""
write to the relavant csv, sorted by factory, fabric , style, colour 2018.11.15

"""
def save_to_csv(order_qty,etd_dict,file_path,last_tisno='TIS18-SO5000'):
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
    lists=[]
    list_shirts=[]
    list_trousers=[]
    for style in order_qty:
        style_value=order_qty.get(style)
        garment_type=style_value.get('garment_type')
        description=style_value.get('description').replace(',',' ') #as target is .csv, the ',' need to be replace
        fabric=style_value.get('fabric')
        fabric_content=style_value.get('fabric_content')
        sheet_type='shirts' #all shirts in one sheet
        if garment_type in ['male_trousers','female_slacks','shorts']:
            sheet_type='trousers'
        filename=file_path+'/{0:%Y} {0:%m} {0:%d} - {1}.csv'.format(datetime.date.today(),sheet_type)
        list_current=locals()['list_'+sheet_type]
        files.append(filename)
        logger.debug(' Start open file %s'%filename)
        sheet_size_title=size_chart.get(sheet_type)
        size_title=size_chart.get(garment_type)

        #if it is new file, write the title
        if not os.path.isfile(filename):
            title=['TIS O/N','ABM Internal O/N','ST','FTY','Ship MON','Style NO.','Commodity','Colours','Units Ordered']
            title.extend(sheet_size_title)
            title.extend(['Freight Way','Shipment Date','ETA Date','Del to Ritemate Warehouse','order & inform to factory','Invoice Ref No.'])
            title.extend(['Fabric','Fabric_content'])
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
            content.extend([fabric,fabric_content])
            logger.debug('assembled content is {0}'.format(content))
            list_current.append(content) #append this line to the corresponding list (list_shirts or list_trousers)
            logger.debug('current list={0}'.format(list_current))
            #write the content


    #sort the list by factory, fabric, style, colour
    from operator import itemgetter
#    sorted_list_shirts=sorted(list_shirts,key=itemgetter(3,5,7)) #coloum 3 is factory, column5 is style , colour 7 is colour
    sorted_list_shirts=sorted(list_shirts,key=itemgetter(3,30,5,7)) #coloum 3 is factory, column5 is style , column 7 is colour, colum 30 is fabric
    logger.debug('After sorted, the list_shirts is {0}'.format(sorted_list_shirts))
    sorted_list_trousers = sorted(list_trousers,key=itemgetter(3,44,5,7))  # coloum 3 is factory, column5 is style , colour 7 is colour, column 44 is fabric
    logger.debug('After sorted, the list_trousers is {0}'.format(sorted_list_trousers))

    #assign TIS No.
    d_new_tisno,assigned_list_shirts,assigned_list_trousers=assign_tisno(sorted_list_shirts,sorted_list_trousers,last_tisno)
    logger.debug('The new TISNo. dict is {0}'.format(d_new_tisno))


    #write sizebreakup to csv
    filename=file_path+'/{0:%Y} {0:%m} {0:%d} - shirts.csv'.format(datetime.date.today())
    for line_no,line in enumerate(assigned_list_shirts):
        try:
            with open(filename, 'a') as data:
                for colnum in range(len(line)-1):
                    print('%s,' % line[colnum], file=data, end='')
                print(line[len(line) - 1], file=data)
        except Exception as err:
            logger.error('Can not write shirts line %s,  error-%s' % (line_no, err))
            continue


    filename=file_path+'/{0:%Y} {0:%m} {0:%d} - trousers.csv'.format(datetime.date.today())
    for line_no,line in enumerate(assigned_list_trousers):
        try:
            with open(filename, 'a') as data:
                for colnum in range(len(line)-1):
                    print('%s,' % line[colnum], file=data, end='')
                print(line[len(line) - 1], file=data)
        except Exception as err:
            logger.error('Can not write trousers line %s,  error-%s' % (line_no, err))
            continue

    #generate tracing sheet
    #combine the shirt list with trousers list and sort by supplier
    list_tracing=[]
    for line_no,line in enumerate(assigned_list_shirts):
        line_tracing=['','Ritemate']
        line_tracing.append(line[3]) #AUWIN
        line_tracing.append(line[5]) #RM1050R
        line_tracing.append(line[0]) #TIS18-SO5092
        line_tracing.append('') # ABM No.
        line_tracing.append('') # Ship code
        line_tracing.append(line[25]) # ETD 14/05/2019
        line_tracing.append(line[26]) #ETA 27/05/2019
        line_tracing.append(line[27]) #DEL 30/05/2019
        line_tracing.append('') #ABM Instore
        line_tracing.append('') #CTM No.
        line_tracing.append(line[6]) #2 Tone Open Front shirt
        line_tracing.append(line[7]) #Blu/Navy
        line_tracing.append(line[8]) #1240
        line_tracing.append('Sea') #Freight mode
        line_tracing.append('') #FOB Port
        line_tracing.append('Brisbane') #ETA Port
        line_tracing.append(line[28]) #today
        line_tracing.append('') #PP sample
        line_tracing.append('') #Shipping sample
        line_tracing.append('') # Test report
        line_tracing.append('"{0}"'.format(line[31])) #14x7 100%cotton ...., add "" to avoid comma, split by csv
        line_tracing.extend(['-','-','-','-']) #volume and 3M
        list_tracing.append(line_tracing)

    for line_no,line in enumerate(assigned_list_trousers):
        line_tracing=['','Ritemate']
        line_tracing.append(line[3]) #AUWIN
        line_tracing.append(line[5]) #RM1002
        line_tracing.append(line[0]) #TIS18-SO5103
        line_tracing.append('') # ABM No.
        line_tracing.append('') # Ship code
        line_tracing.append(line[39]) # ETD 14/05/2019
        line_tracing.append(line[40]) #ETA 27/05/2019
        line_tracing.append(line[41]) #DEL 30/05/2019
        line_tracing.append('') #ABM Instore
        line_tracing.append('') #CTM No.
        line_tracing.append(line[6]) #drill trousers
        line_tracing.append(line[7]) #Navy
        line_tracing.append(line[8]) #1000
        line_tracing.append('Sea') #Freight mode
        line_tracing.append('') #FOB Port
        line_tracing.append('Brisbane') #ETA Port
        line_tracing.append(line[42]) #today
        line_tracing.append('') #PP sample
        line_tracing.append('') #Shipping sample
        line_tracing.append('') # Test report
        line_tracing.append('"{0}"'.format(line[45])) #14x7 100%cotton ...., add "" to avoid comma, split by csv
        line_tracing.extend(['-','-','-','-']) #volume and 3M
        list_tracing.append(line_tracing)

    sorted_list_tracing=sorted(list_tracing,key=itemgetter(4,3,13)) #sorted by TISNO->STYLE->COLOUR
    logger.debug('sorted tracing list is {0}'.format(sorted_list_tracing))

    title = ['','Customer','Supplier','Style NO.','TIS O/N', 'ABM Internal O/N', 'ShipCode', 'Shipment Date', 'ETA Date', 'Del to RM Warehouse','ABM InStore','CTM O/N','Commodity','Colours','Quantity','Freight','FOBPort','ETAPort','OrderDate','PPSample','ShippingSample','TestReport','Fabric']
    filename=file_path+'/{0:%Y} {0:%m} {0:%d} - tracing.csv'.format(datetime.date.today())
    #write title
    try:
        with open(filename, 'w') as data:
            for colnum in range(len(title) - 1):
                print('%s,' % title[colnum], file=data, end='')
            print(title[len(title) - 1], file=data)  # for the last column without ',' following
    except Exception as err:
        logger.error('Can not open file %s,  error-%s' % (filename, err))

    #write content
    for line_no,line in enumerate(sorted_list_tracing):
        try:
            with open(filename, 'a') as data:
                for colnum in range(len(line)-1):
                    print('%s,' % line[colnum], file=data, end='')
                print(line[len(line) - 1], file=data)
        except Exception as err:
            logger.error('Can not write tracing line %s,  error-%s' % (line_no, err))
            continue


    return files

def get_o_dict(list_garment):
    o_dict=OrderedDict()
    for line in list_garment:
        supplier=line[3]
        style=line[5]
        if supplier not in o_dict: #when come accross new supplier , then add one item
            value=[style] #create the new value list with style for the new supplier first time : ['RM1050']
            o_dict[supplier]=value #{'Auwin':['RM1050R']}
        else: #when the supplier is already exist, then add the style to the value list
            value=o_dict.get(supplier) #['RM1050R']
            if style not in value: #when come accross the new style for this supplier, then add to the list
                value.append(style) #['RM1050R','RM107V2']
                o_dict[supplier]=value ##{'Auwin':['RM1050R','RM107V2']}
    return o_dict

"""
Assign TISNO. for size breakup shirts and pants, required the successive No. to shirts and pants for one supplier.
"""
def assign_tisno(list_shirts,list_trousers,last_no='TIS18-SO5000'):
    #build 2 new ordereddict to store the list with only supplier and style distinct
    o_dict_shirts=get_o_dict(list_shirts)
    logger.debug('the o_dict_shirts is {0}'.format(o_dict_shirts))
    o_dict_trousers=get_o_dict(list_trousers)
    logger.debug('the o_dict_trousers is {0}'.format(o_dict_trousers))

    #combine 2 o_dict with same supplier
    for supplier,value in o_dict_trousers.items(): #iterate trousers
        if supplier in o_dict_shirts: #if the supplier of trouser alread in shirt, just append the style of trouser to shirts
            o_dict_shirts[supplier].extend(o_dict_trousers.get(supplier))
        else: #otherwise, then create a supplier in the last of the o_dict_shirts. For example , Tanhoo only make trousers not shirts, then there is no supplier in shirts
            o_dict_shirts[supplier]=o_dict_trousers.get(supplier)
    logger.debug('after combine the o_dict is {0}'.format(o_dict_shirts))

    #calculate TISNO to a OrderedDict with 1 increasment to every style
    tis_prefix=last_no[:8]
    current_no=int(last_no[8:])
    assigned_dict=OrderedDict()
    for supplier,l_style in o_dict_shirts.items():
        for style in l_style:
            current_no+=1
            assigned_dict['{0}+{1}'.format(supplier,style)]='{0}{1}'.format(tis_prefix,current_no)#assigned_dict['TANHOO+RM1040R']='TIS18-SO5003'

    #assign the TISNO to the list of shirts and trousers
    for line_no,line in enumerate(list_shirts):
        key='{0}+{1}'.format(line[3],line[5]) #key='TANHOO+RM1040R'
        tis_no=assigned_dict.get(key) #tis_no='TIS18-SO5003'
        list_shirts[line_no][0]=tis_no

    for line_no,line in enumerate(list_trousers):
        key='{0}+{1}'.format(line[3],line[5]) #key='TANHOO+RM1004R'
        tis_no=assigned_dict.get(key) #tis_no='TIS18-SO5009'
        list_trousers[line_no][0]=tis_no

    #write dict for tracing sheet with key as supplier
    dict_tracing=OrderedDict()


    return assigned_dict,list_shirts,list_trousers



"""

"""
def parse_requisition(cell_list=[],filename='',sheetname='',etd_dict={},file_path='',last_tisno='TIS18-SO5000'):
    order=read_eachline(cell_list=cell_list,filename=filename,sheetname=sheetname)
    result=save_to_csv(order,etd_dict,file_path=file_path,last_tisno=last_tisno)
    return result
        

    
