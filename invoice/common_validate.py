import os
from TISProduction import tis_log
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
    msg = '\nStart verify {0} {1}'.format(file, by_name)
    l_msg_success.append(msg)
    l_msg_error = []
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
            l_msg_error.append()
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

    # return all_summary_correct
    result = {'msg_success': l_msg_success, 'msg_error': l_msg_error, 'total_carton': packing_list.get('total_carton')}
    return result

