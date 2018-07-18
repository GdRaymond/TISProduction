import numpy as np
from invoice.models import Packing,Actual_quantity
from invoice.inv_pack import MessageList
from TISProduction.tis_log import get_tis_logger

logger=get_tis_logger()

def get_style_size_quantity(style,colour): #colour: SUM-Add all quantity, All-iterate every colour , colour name-
    msg_list=MessageList()
    msg='Start to get size quantity matrix for {0}-{1}'.format(style,colour)
    msg_list.save_msg(msg)
    l_invoice_size_quantity=[]
    # Get all packing according to style
    packings=Packing.objects.filter(style__iexact=style).order_by('invoice_date')
    for packing in packings:
        msg='==Invoice No. {0}, Invoice_date {1}'.format(packing.invoice_no,packing.invoice_date)
        msg_list.save_msg(msg)
        if colour in ['SUM','ALL']:
            actual_qtys=Actual_quantity.objects.filter(packing=packing)
        else:
            actual_qtys=Actual_quantity.objects.filter(packing=packing,colour__iexact=colour)
        l_size_quantity=[]
        for actual_qty in actual_qtys:
            size_quantity=[]
            #get all colour belonging to this packing item
            for i in range(30):
                size_quantity.append(getattr(actual_qty,'size{0}'.format(i+1))) #[qtysize1,qtysize2...,qtysize30]
            logger.debug('      size_quantity for {0} is {1}'.format(actual_qty.colour,size_quantity))
            l_size_quantity.append(size_quantity)
            msg='       Finish colour {0}'.format(actual_qty.colour)
            msg_list.save_msg(msg)
        if not l_size_quantity:
            msg='   l_size_quantity is none for this invoice, skip'
            msg_list.save_msg(msg)
            continue
        logger.debug('  l_size_quantity is {0}'.format(l_size_quantity))
        #sum the list
        l_size_quantity=list(np.sum(l_size_quantity,axis=0))
        logger.debug('  After sum l_size_quantity is {0}'.format(l_size_quantity))
        #insert invoice date and invoice NO. to begining and ending, [2018-01-01,qtysize1,...qtysize30,'AW18F201']
        l_size_quantity.insert(0,packing.invoice_date)
        l_size_quantity.insert(-1,packing.invoice_no)
        l_invoice_size_quantity.append(l_size_quantity)
        msg='   Finish this Invoice'
        msg_list.save_msg(msg)
    #Below conbine the line with same invoice_date, because there are different orders of same style in one invoice, like adding order
    pre_line=l_invoice_size_quantity[0]
    for i,line in enumerate(l_invoice_size_quantity):
        if i==0:
            continue
        if pre_line[0]==line[0]:
            pass
        pre_line=line

    msg='==Finish All get list={0}'.format(l_invoice_size_quantity)
    msg_list.save_msg(msg)
    return l_invoice_size_quantity,msg_list