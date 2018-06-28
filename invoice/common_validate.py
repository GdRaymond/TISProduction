import os,re
from TISProduction import tis_log
from excelway.tis_excel import TIS_Excel
logger=tis_log.get_tis_logger()


base_dir=os.path.abspath(os.path.dirname(__file__))


"""from detail to calculate the summary
   return: summary_by_cal={'-Cobalt blue':{'total':, 'size_qty'{'-2xs':,...}},
                           ...
                          }
"""


def calculate_detail(packing_list={}, file='test.xlsx', by_name="RM500BT(TIS16-SO3466)"):
    logger.debug('======================================')
    logger.debug('Start calculate_detail and validate detail')
    detail_correct = True
    summary_by_cal = {}  # init the result dict
    list_carton_no_from = []
    list_carton_no_to = []
    carton_total_by_cal = 0

    logger.debug('-Start  validate carton No. in each line')
    all_correct = True
    for line in packing_list.get('detail'):
        # validate the carton No. and quantity
        carton_no_from = line.get('from')
        carton_no_to = line.get('to')
        carton_line_total = line.get('carton_qty')
        if carton_line_total != (carton_no_to - carton_no_from + 1):
            logger.error('--%s - %s - Carton No. wrong at line from:%s to:%s total:%s ' % (
            file, by_name, carton_no_from, carton_no_to, carton_line_total))
            all_correct = False

            # put the carton no to list and accumulate the carton qty
        list_carton_no_from.append(carton_no_from)
        list_carton_no_to.append(carton_no_to)
        carton_total_by_cal += carton_line_total

        colour = line.get('colour_detail')
        temp_dict = summary_by_cal.get(colour)
        if temp_dict is None:
            temp_dict = {}
        temp_size_qty = temp_dict.get('size_qty')
        if temp_size_qty is None:
            temp_size_qty = {}
        for size in line.get('size_qty'):
            # print("====in colour=%s, size=%s , carton qty=%s, per carton=%s "%(colour,size,line.get('to')-line.get('from')+1,line.get('size_qty').get(size)))
            base_qty = temp_size_qty.get(size)
            if base_qty is None:
                base_qty = 0
            try:
                temp_size_qty[size] = base_qty + carton_line_total * line.get('size_qty').get(size)
            except Exception as err:
                logger.error(
                    '--%s - %s - detail line cal error at from=%s to=%s. base_qty=%s, carton_line_total=%s,size_qty[%s]=%s'
                    % (file, by_name, carton_no_from, carton_no_to, base_qty, carton_line_total, size,
                       line.get('size_qty').get(size)))
        temp_dict['size_qty'] = temp_size_qty
        temp_dict['total'] = 0
        summary_by_cal[colour] = temp_dict
    if all_correct:
        logger.debug('--Correct of carton No. in each line ')
    else:
        detail_correct = False

    # validate the consistency of no. and quantity by iterate\ing the carton no list
    all_correct = True
    logger.debug('-Start validate the consistency of carton no.')
    for no in range(0, len(list_carton_no_from) - 1):
        if float(list_carton_no_from[no + 1]) != float(list_carton_no_to[no]) + 1:
            all_correct = False
            logger.error('--%s - %s - Carton No. not consistant at line to:%s next from:%s  ' \
                         % (file, by_name, list_carton_no_to[no], list_carton_no_from[no + 1]))
    if all_correct:
        logger.debug('--Correct of the consistency of carton No. ')
    else:
        detail_correct = False

    if detail_correct:
        logger.debug('-Correct detail carton No.')

    # validate the carton quantity
    logger.debug('========================================')
    logger.debug('Start validate the total carton quantity')
    if carton_total_by_cal == packing_list.get('total_carton'):
        logger.debug('-Correct of he total carton quantity.')
    else:
        logger.error('-%s-%s-Wrong of the total carton, in sheet - %s, but by calculation - %s' \
                     % (file, by_name, packing_list.get('total_carton'), carton_total_by_cal))

    for item in summary_by_cal:
        temp_dict = summary_by_cal.get(item)
        temp_total = temp_dict.get('total')
        for size in temp_dict.get('size_qty'):
            temp_total += temp_dict.get('size_qty').get(size)
        temp_dict['total'] = temp_total
        summary_by_cal[item] = temp_dict
    return summary_by_cal


# validate the summary with detail
def validate_summary(packing_list={}, file='test.xlsx', by_name="RM500BT(TIS16-SO3466)"):
    # calculate detail
    detail = calculate_detail(packing_list=packing_list, file=file, by_name=by_name)

    all_summary_correct = True
    logger.debug('======================================')
    logger.debug('Start validate summary')
    # validate sumary on ratio and balance
    value_summary = packing_list.get('summary')
    l_msg_success = []
    msg = 'Start verify {0} {1}'.format(file, by_name)
    l_msg_success.append(msg)
    l_msg_error = []
    l_msg_recap=[]
    l_msg_recap.append('')
    l_msg_recap.append(msg)
    for colour in value_summary:
        value_colour = value_summary.get(colour)

        # validate the ratio, find the ration greater than 5% and balance greater than 10pcs
        logger.debug('-Start validate the ratio for colour:%s , checking if ratio> %%5 and balance>10pcs' % (colour))
        all_correct = True
        try:
            ratio = value_colour.get('Ratio').get('size_qty')
            balance = value_colour.get('Balance').get('size_qty')
        except Exception as err:
            msg = '--%s - %s - Ratio or balance can not find, error--%s' \
                  % (file, by_name, err)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        balance_by_cal = 0
        for size in ratio:
            ratio_value = ratio.get(size)
            balance_value = balance.get(size)
            balance_by_cal += balance_value
            # logger.debug('size:%s--ratio:%s'%(size,ratio_value))
            if str(ratio_value).strip() != "" and ratio_value > 0.05 \
                    and str(balance_value).strip() != "" and balance_value > 9:
                msg = '--%s - %s - Ratio warning at colour:%s size:%s - ratio: %s, balance:%s' \
                      % (file, by_name, colour, size, ratio_value, balance_value)
                logger.error(msg)
                l_msg_error.append(msg)
                all_correct = False
        if balance_by_cal != value_colour.get('Balance').get('total'):
            msg = '--%s-%s - Balance total is not correct at colour: %s, in doc=%s, cal=%s' \
                  % (file, by_name, colour, value_colour.get('Balance').get('total'), balance_by_cal)
            logger.error(msg)
            l_msg_error.append(msg)
            all_correct = False
        if all_correct:
            msg = '--The total balance is correct and  ratio for colour: %s is ok without exceeding 5%% and balance greater than 10pcs' % colour
            logger.debug(msg)
            l_msg_success.append(msg)
        else:
            all_summary_correct = False

    # validate summary the quantity  comparing with detail quantity : 1- colour from summary to detail
    logger.debug('-Start validate the quantity for colour:, summary-> detail')
    summary_correct = True
    summary_total_qty = 0
    for colour in value_summary:
        logger.debug('--Start validate the quantity for colour:%s, summary-> detail' % colour)
        all_correct = True
        value_colour = value_summary.get(colour)

        """
          if the Actual Qty name is varied, like LM17ZF202-ob-sox, the name is BY SEA, then error here
        if by_name=='RM301EWS(TIS15-SO3127)':
            logger.error('RM301EWS(TIS15-SO3127)--value_colour %s'%value_colour)
        """

        try:
            actual_qty = value_colour.get('Actual Qty')
            summary_total_qty += actual_qty.get('total')
            actual_qty_size_qty = actual_qty.get('size_qty')
        except Exception as e:
            msg = '---%s - %s - Can not find Actual Qty name: %s' % (file, by_name, e)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        """
          if the colour name in detail not consistant with summary, error will occur
          for example, in LM16ZF214-SO3469, coulur in detail is INK, in summary is INK NAVY
        """
        if detail.get(colour) is None:
            msg = '---%s - %s - Can not find colour:%s in detail ' \
                  % (file, by_name, colour)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        detail_size_qty = detail.get(colour).get('size_qty')
        # validate the actural qty , 1.1 - size from summary to detail
        total_by_cal = 0
        for size in actual_qty_size_qty:
            actual_qty_size_qty_value = actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip() != "":
                # logger.debug('---%s - %s - Qty data at colour:%s size:%s - size qty: %s, temp total:%s'\
                #  %(file,by_name,colour,size,actual_qty_size_qty_value,total_by_cal))
                total_by_cal += actual_qty_size_qty_value

                if actual_qty_size_qty_value != detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size) == 0) or \
                            (actual_qty_size_qty_value == 0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg = '---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s' \
                          % (file, by_name, colour, size, actual_qty_size_qty_value, detail_size_qty.get(size))
                    logger.error(msg + ' Colour:sum->detai size:sum->detal')
                    l_msg_error.append(msg)
                    all_correct = False
                    summary_correct = False

        # validate the actual qty total, comparing with calculation
        if actual_qty.get('total') != total_by_cal:
            msg = '---%s - %s - Actual qty total warning at colour:%s  - in doc: %s, by calculation:%s' \
                  % (file, by_name, colour, actual_qty.get('total'), total_by_cal)
            logger.error(msg)
            l_msg_error.append(msg)

        # validate the actural qty , 1.2 - size from detail to summary
        for size in detail_size_qty:
            actual_qty_size_qty_value = actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip() != "":
                if actual_qty_size_qty_value != detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size) == 0) or \
                            (actual_qty_size_qty_value == 0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg = '---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s' \
                          % (file, by_name, colour, size, actual_qty_size_qty_value, detail_size_qty.get(size))
                    logger.error(msg + ' Colour:sum->detai size:detail->sum')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct = False
                    summary_correct = False

        if all_correct:
            msg = '---Correct: the quantity for colour:%s, summary-> detail ' % colour
            logger.debug(msg)
            l_msg_success.append(msg)
    if summary_correct:
        msg = '--All Correct: the quantity colour summary-> detail '
        logger.debug(msg)
        l_msg_success.append(msg)
    else:
        all_summary_correct = False

    # validate summary the quantity  comparing with detail quantity : 2- colour from detail to summary
    logger.debug('-Start validate the quantity for colour, detail-> summary')
    summary_correct = True
    for colour in detail:
        logger.debug('--Start validate the quantity for colour:%s, detail-> summary' % colour)
        all_correct = True
        value_colour = value_summary.get(colour)

        """
          if the colour name in detail not consistant with summary, error will occur
          for example, in LM16ZF214-SO3469, coulur in detail is INK, in summary is INK NAVY
        """
        if value_colour is None:
            msg = '---%s - %s - Can not find colour:%s in summary ' \
                  % (file, by_name, colour)
            logger.error(msg)
            l_msg_error.append(msg)
            continue

        try:
            actual_qty = value_colour.get('Actual Qty')
            actual_qty_size_qty = actual_qty.get('size_qty')
        except Exception as e:
            msg = '---%s-%s-Can not find Actural Qty name - %s' % (file, by_name, e)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        detail_size_qty = detail.get(colour).get('size_qty')
        # validate the actural qty , 2.1 - size from summary to detail
        for size in actual_qty_size_qty:
            actual_qty_size_qty_value = actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip() != "":
                if actual_qty_size_qty_value != detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size) == 0) or \
                            (actual_qty_size_qty_value == 0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg = '---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s' \
                          % (file, by_name, colour, size, actual_qty_size_qty_value, detail_size_qty.get(size))
                    logger.error(msg + ' Colour:detail->sum size:sum->detail')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct = False
                    summary_correct = False

        # validate the actural qty , 2.2 - size from detail to summary
        for size in detail_size_qty:
            actual_qty_size_qty_value = actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip() != "":
                if actual_qty_size_qty_value != detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size) == 0) or \
                            (actual_qty_size_qty_value == 0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg = '---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s' \
                          % (file, by_name, colour, size, actual_qty_size_qty_value, detail_size_qty.get(size))
                    logger.error(msg + ' Colour:detail->sum size:detail->sum')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct = False
                    summary_correct = False

        if all_correct:
            msg = '---Correct: the quantity for colour:%s, detail-> summary ' % colour
            logger.debug(msg)
            l_msg_success.append(msg)
    if summary_correct:
        msg = '--All Correct: the quantity colour detail-> summary '
        logger.debug(msg)
        l_msg_success.append(msg)
    else:
        all_summary_correct = False

    # validate total quantity in doc comparing with sum of each colour in summary
    logger.debug('-Start validate total quantity ')
    if packing_list.get('total_quantity') != summary_total_qty:
        msg = '--%s - %s -Validate total quantity Wrong: in doc:%s - sum  in summary %s ' \
              % (file, by_name, packing_list.get('total_quantity'), summary_total_qty)
        logger.error(msg)
        l_msg_error.append(msg)
        all_summary_correct = False

    else:
        msg = '--Validate total quantity Correct'
        logger.debug(msg)
        l_msg_success.append(msg)

    if all_summary_correct:
        msg = '-All correct of summary'
        logger.debug(msg)
        l_msg_success.append(msg)
        l_msg_recap.append(msg)
    else:
        l_msg_recap.extend(l_msg_error)
    try:
        quantity_info='Order:{0} style:{1} {2:d} cartons total:{3:d}pcs'.format(packing_list.get('TISNo'),packing_list.get('Style'),
                                                                      int(packing_list.get('total_carton')),int(packing_list.get('total_quantity')))
        for colour_key,colour_value in packing_list.get('summary').items():
            colour_quantity=int(colour_value.get('Actual Qty').get('total'))
            quantity_info='{0} {1}:{2:d} '.format(quantity_info,colour_key,colour_quantity)
        l_msg_recap.append(quantity_info)
    except Exception as e:
        logger.error('error when get quantity from packing list:{0}'.format(e))


    # return all_summary_correct
    result = {'msg_success': l_msg_success, 'msg_error': l_msg_error, 'msg_recap':l_msg_recap,'total_carton': packing_list.get('total_carton')}
    return result

def search_field(cell_list,key_patterns,value_pattern):
    logger.debug('start to search field {0} validated with {1}'.format(key_patterns,value_pattern))
    nrows, ncols=len(cell_list),len(cell_list[0])
    found=False
    status='Finished'
    start_row=None
    field_col=None
    for row in range(nrows):
        for col in range(ncols):
            current_cell=str(cell_list[row][col]).strip()
            for key_pattern in key_patterns: #there may be different key in suppliers, lie quantity, qty
                match=re.search(key_pattern,current_cell,re.I)
                if match: #if some cell contain key_pattern('order'), search under cell of same colume , if contain value_pattern('TIS18-' then regard as order column
                    for row_under in range(row,nrows):
                        cell_under=str(cell_list[row_under][col]).strip()
                        match_under=re.search(value_pattern,cell_under,re.I)
                        if match_under:
                            field_col=col
                            if field_col == 0:
                                logger.warn('!!!Maybe not correct')

                            found=True
                            break
                if found:
                    break
            if found:
                break
        if found:
            start_row=row
            break
    else: #finish iteration, can't find then pop error
        status='Can not find the colum No. of {0}'.format(key_patterns)
        logger.error(status)
    result={'status':status,'start_row':start_row,'field_col':field_col}
    logger.info('get result {0}'.format(result))
    return result

def get_horizontal_field(cell_list,key_patterns,value_pattern):
    logger.debug('start to search field {0} validated with {1}'.format(key_patterns,value_pattern))
    nrows, ncols=len(cell_list),len(cell_list[0])
    found=False
    status='Finished'
    field_row=None
    field_col=None
    content=None
    for row in range(nrows):
        for col in range(ncols):
            current_cell=str(cell_list[row][col])
            for key_pattern in key_patterns: #there may be different key for suppliers, like Invoice No. Inv No.
                match=re.search(key_pattern,current_cell,re.I)
                if match: #if some cell contain key_pattern('Inv No.'), search right side cell of same row , if contain value_pattern('AW-' then regard as order column
                    for col_right in range(col+1,ncols):
                        cell_under=str(cell_list[row][col_right])
                        match_right=re.search(value_pattern,cell_under,re.I)
                        if match_right:
                            field_col=col
                            content=cell_under
                            found=True
                            break
                if found:
                    break
            if found:
                break
        if found:
            field_row=row
            break
    else: #finish iteration, can't find then pop error
        status='Can not find the colum No. of {0}'.format(key_patterns)
        logger.error(status)
    result={'status':status,'field_row':field_row,'field_col':field_col,'content':content}
    logger.info('get result {0}'.format(result))
    return result

def get_total(cell_list,key_patterns,value_pattern,start_row,field_col):
    logger.debug('start to search field {0} validated with {1}'.format(key_patterns,value_pattern))
    nrows, ncols=len(cell_list),len(cell_list[0])
    found=False
    status='Finished'
    field_row=None
    content=None
    for row in range(start_row,nrows):
        for col in range(ncols):
            current_cell=str(cell_list[row][col])
            for key_pattern in key_patterns: #there may be different key for suppliers, like total, sum
                match=re.search(key_pattern,current_cell,re.I)
                if match: #if some cell contain key_pattern('Inv No.'), search right side cell of same row , if contain value_pattern('AW-' then regard as order column
                    cell_field=str(cell_list[row][field_col])
                    match_field=re.search(value_pattern,cell_field,re.I)
                    if match_field:
                        content=cell_field
                        found=True
                        break
                if found:
                    break
            if found:
                break
        if found:
            field_row=row
            break
    else: #finish iteration, can't find then pop error
        status='Can not find the colum No. of {0}'.format(key_patterns)
        logger.error(status)
    result={'status':status,'field_row':field_row,'field_col':field_col,'content':content}
    logger.info('get result {0}'.format(result))
    return result

def get_cell_range_content(cell_list,row,col,updown):
    '''
    try to get the cell in the range of row, row-1 , row+1
    :param cell_list:
    :param row:
    :param col:
    :param range:
    :return:
    '''
    result=str(cell_list[row][col]).strip()
    for i in range(1,updown+1):
        if not result and row-i>=0:
            result=str(cell_list[row-i][col]).strip()
        if not result:
            result=str(cell_list[row+1][col]).strip()
    return result



def parse_invoice(cell_list=[],filename='',sheetname='',save_db=False,supplier=''):
    status='Finished'
    l_msg_success=[]
    l_msg_error=[]
    l_msg_recap=[]
    result_validate={'status':status,'msg_success':l_msg_success,'msg_error':l_msg_error,'msg_recap':l_msg_recap}
    l_msg_recap.append('')
    msg_success='=============Start to verify invoice {0} sheet {1}================'.format(filename,sheetname)
    l_msg_recap.append(msg_success)
    if not cell_list:
        msg_error = 'Regarding sheet: {0} ,Can not read this sheet or sheet is blank'.format(sheetname)
        l_msg_error.append(msg_error)
        l_msg_recap.append(msg_error)
        result_validate = {'status': 'Failed','msg_error':l_msg_error,'msg_recap':l_msg_recap}
        return result_validate
    nrows = len(cell_list)
    ncols = len(cell_list[0])
    invoice = {}
    invoice["detail"] = []
    detail_seg = False
    col_order_no = None
    col_style=None
    col_qty = None
    col_price = None
    col_amount = None
    order_start_row=0
    status='Finished'

    #locate the coloumn and row Nnumber of order
    key_patterns=[('order')]
    value_pattern_order=('(TIS\d{2}-S[0O]\d{4}\w?)') #TIS18-SO1234a
    field_location=search_field(cell_list,key_patterns,value_pattern_order)
    order_start_row = field_location.get('start_row')
    col_order_no=field_location.get('field_col')
    if not order_start_row or not col_order_no:
        msg_error = 'Can not locate the order NO., please check if the title contain wording "order"'
        l_msg_error.append(msg_error)
        l_msg_recap.append(msg_error)
        result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                           'msg_success': l_msg_success}
        return result_validate

    #locate the coloumn and row Nnumber of style
    key_patterns=[(r'style no\.?$')]
    value_pattern=('\w+')
    field_location=search_field(cell_list,key_patterns,value_pattern)
    col_style=field_location.get('field_col')
    #if not col_style:
        #status = 'Can not locate the style No., please check if the title contain wording "style no"'
        #result_validate = {'status': status}
        #return result_validate

    #locate the coloumn and row Nnumber of clour, only Tanhoo has the colour
    key_patterns=[('color')]
    value_pattern=('\w+')
    field_location=search_field(cell_list,key_patterns,value_pattern)
    col_colour=field_location.get('field_col')


    #locate the column and row number of quantity
    key_patterns=[(r'\bqty'),(r'\bquantity'),(r'\bcount')]
    value_pattern_quantity=('^((\d+)|(\d+\.\d+))$') #the cell will be read as float to str, like 410.0,so compatible with int and float
    try:
        #pass
        field_location=search_field(cell_list,key_patterns,value_pattern_quantity)
        col_qty=field_location.get('field_col')
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))
    if not col_qty:
        msg_error = 'Can not locate the quantity, please check if the title contain wording "qty" or "quantity" or "count"'
        l_msg_error.append(msg_error)
        l_msg_recap.append(msg_error)
        result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                           'msg_success': l_msg_success}
        return result_validate

    #locate the column and row number of price
    key_patterns=[(r'(unit)?\bprice')]
    value_pattern_price=('^(\$?(\d+)|(\d+\.\d+))$') #some with $ , some without
    try:
        #pass
        field_location=search_field(cell_list,key_patterns,value_pattern_price)
        col_price=field_location.get('field_col')
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))
    if not col_price:
        msg_error = 'Can not locate the price, please check if the title contain wording "price"'
        l_msg_error.append(msg_error)
        l_msg_recap.append(msg_error)
        result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                           'msg_success': l_msg_success}
        return result_validate


    #locate the column and row number of amount
    key_patterns=[(r'\bamount'),(r'\btotal value')]
    value_pattern_amount=('^(\$?(\d+)|(\d+\.\d+))$') #some with $ , some without
    try:
        #pass
        field_location=search_field(cell_list,key_patterns,value_pattern_amount)
        col_amount=field_location.get('field_col')
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))
    if not col_amount:
        msg_error = 'Can not locate the amount of each order, please check if the title contain wording "amount" or "total value"'
        l_msg_error.append(msg_error)
        l_msg_recap.append(msg_error)
        result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                           'msg_success': l_msg_success}
        return result_validate


    #below iterate the line of order to get order style colour
    l_detail=[] #[{'tis_no':,'style':,'colour':,'quantity':,'price':,'amount':},{}]
    total_amount_from_detail = 0
    for row in range(order_start_row,nrows):
        #get order NO.
        content=str(cell_list[row][col_order_no])
        match=re.search(value_pattern_order,content,re.I)
        if not match:
            continue
        detail_info={}
        tis_no=match.group(1)
        detail_info['TISNo']=tis_no

        #get style No.
        if not col_style: # For Auwin and Jinfeng , the style No. is following the tis no with / or , TIS18-SO1234/RM1004
            content=str(cell_list[row][col_order_no]).strip()
            match=re.search(r'.*TIS\d{2}-SO\d{4}\w?\W(.*)$',content,re.I)
            if match:
                style=str(match.group(1)).strip().upper()
        else: #For other supplier who has the style column
            style=str(cell_list[row][col_style]).strip().upper()
        if not style:
            msg_error = 'Can not find the style No. for order {0}'.format(tis_no)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)
            result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                               'msg_success': l_msg_success}
            return result_validate
        detail_info['Style']=style

        #get colour
        if not col_style: # For all supplier exept Tanhoo , there is no colour column, so set to 'ALL'
            colour='ALL'
        else: #For other supplier who has the style column
            colour=str(cell_list[row][col_colour]).strip().upper()
        detail_info['colour']=colour

        #get quantity.
        content=str(get_cell_range_content(cell_list,row,col_qty,1))
        match=re.search(value_pattern_quantity,content,re.I)
        if not match:
            msg_error = 'Can not find the quantiy. for order {0}'.format(tis_no)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)
            result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                               'msg_success': l_msg_success}
            return result_validate
        quantity=int(float(match.group(1)))
        detail_info['quantity']=quantity

        #get price.
        content=str(get_cell_range_content(cell_list,row,col_price,1))
        match=re.search(value_pattern_price,content,re.I)
        if not match:
            msg_error = 'Can not find the price. for order {0}'.format(tis_no)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)
            result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,
                               'msg_success': l_msg_success}
            return result_validate
        price=float(match.group(1))
        detail_info['price']=price

        #get amount and accumulate
        content=str(get_cell_range_content(cell_list,row,col_amount,1))
        match=re.search(value_pattern_amount,content,re.I)
        if not match:
            msg_error = 'Can not find the amount. for order {0}'.format(tis_no)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)
            result_validate = {'status': 'Failed', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap}
            return result_validate
        amount=round(float(match.group(1)),2) #100.00
        total_amount_from_detail+=amount
        detail_info['amount']=amount

        #verify the amount, compare with quantity x price
        if amount==round((quantity*price),2):
            msg_success='verfy line successfully order {0} colour {1} amount={2} ={3} x {4}'.format(tis_no,colour,amount,price,quantity)
            logger.info(msg_success)
            l_msg_success.append(msg_success)
            l_msg_recap.append(msg_success)
        else:
            msg_error='Veriry line error  , order {0} colour {1} amount={2} not={3} x {4}'.format(tis_no,colour,amount,price,quantity)
            logger.error(msg_error)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)

        #add to list
        l_detail.append(detail_info)
    logger.debug('get l_detail={0}'.format(l_detail))

    #fetch the invoice No.
    key_patterns=[(r'invoice no'),('inv no')]
    value_pattern=('\w+')
    try:
        #pass
        invoice_no=get_horizontal_field(cell_list,key_patterns,value_pattern).get('content')
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))

    #fetch the invoice date.
    key_patterns=[(r'date'),]
    value_pattern=('\w+')
    try:
        #pass
        invoice_date=get_horizontal_field(cell_list,key_patterns,value_pattern).get('content')
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))


    #fetch the total quantity.
    key_patterns=[(r'total')]
    value_pattern = ('^((\d+)|(\d+\.\d+))$')  # the cell will be read as float to str, like 410.0,so compatible with int and float
    try:
        #pass
        total_quantity=get_total(cell_list,key_patterns,value_pattern,order_start_row,col_qty).get('content')
        if total_quantity:
            total_quantity=int(float(total_quantity))
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))

    #fetch the total amount.
    key_patterns=[(r'total')]
    value_pattern=('^\$?(USD)?((\d+)|(\d+\.\d+))$') #some with $ , some without
    try:
        #pass
        total_amount=0 #initialize to 0, in case of exception
        total_amount=get_total(cell_list,key_patterns,value_pattern,order_start_row,col_amount).get('content')
        total_amount=round(float(total_amount),2)
        if total_amount==round(total_amount_from_detail,2):
            msg_success='Verify total amount comparing with sum of order amount successfully ={0}'.format(total_amount)
            l_msg_success.append(msg_success)
            l_msg_recap.append(msg_success)
        else:
            msg_error='Verify total amount error total={0}, sum of orders amount={1}'.format(total_amount,total_amount_from_detail)
            l_msg_error.append(msg_error)
            l_msg_recap.append(msg_error)
    except Exception as e:
        logger.error('error when search field: {0}'.format(e))

    #assemble invoice ino
    #consolidate the invoice detail list to dict 2 level by , TIS no, style, colour,
    # {'TIS18-SO1234':{'RM1004':[{'colour':'Ora/Nav','price':,'quantity':}}]},}
    logger.debug('before consolidate l_detaile={0}'.format(l_detail))
    d_detail=TIS_Excel.consolidate_order(l_detail)
    logger.debug('after consolidate d_detaile={0}'.format(d_detail))
    invoice_info={'invoice_no':invoice_no,'total_amount':total_amount,'date':invoice_date,'total_quantity':total_quantity,'detail':d_detail}



    msg_success = 'Finish Verify invoice {0} sheet {1}'.format(filename,sheetname)
    l_msg_success.append(msg_success)
    l_msg_recap.append(msg_success)
    result_validate = {'status': 'Finished', 'msg_error': l_msg_error, 'msg_recap': l_msg_recap,'msg_success':l_msg_success}

    return result_validate,invoice_info