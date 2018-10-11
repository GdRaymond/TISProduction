import numpy as np
from invoice.models import Packing,Actual_quantity
from invoice.inv_pack import MessageList
from TISProduction.tis_log import get_tis_logger
from matplotlib import pyplot as plt
from products.size_chart import get_size_list
import pandas as pd
from pandas import DataFrame as pandasDataFrame

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
        l_size_quantity.append(packing.invoice_no)
        l_invoice_size_quantity.append(l_size_quantity)
        msg='   Finish this Invoice'
        msg_list.save_msg(msg)
    #Below conbine the line with same invoice_date, because there are different orders of same style in one invoice, like adding order
    pre_line=l_invoice_size_quantity[0]
    for i,line in enumerate(l_invoice_size_quantity):
        if i==0:
            continue
        if pre_line[0]==line[0]:
            tmp_size_quantity=np.array(l_invoice_size_quantity)[i-1:i+1,1:-1] #transform to numpy array and slice to get the 2 line of size quantity
            msg='   same style different orders({0} & {1}) in same invoice:{2} , and combine them'.format(i-1,i,tmp_size_quantity)
            msg_list.save_msg(msg)
            sum_size_quantity=list(np.sum(tmp_size_quantity,axis=0))
            pre=l_invoice_size_quantity.pop(i-1)
            logger.debug('  pop pre_line {0}'.format(pre))
            pre=l_invoice_size_quantity.pop(i-1)            #because preline has been pop, so the then current line get the i-1
            logger.debug('  pop next_line {0}'.format(pre))
            line=[pre_line[0]]
            line.extend(sum_size_quantity)
            line.append(pre_line[-1]) #add invoice_date and invoice_no
            logger.debug('  get new line {0}'.format(line))
            l_invoice_size_quantity.insert(i-1,line)
        pre_line=line

    sub_total=np.sum(np.array(l_invoice_size_quantity)[:,1:-1],axis=1)
    logger.debug('get sub_total {0}'.format(sub_total))
    l_invoice_size_quantity=np.insert(l_invoice_size_quantity,len(l_invoice_size_quantity[0])-1,sub_total,axis=1)
    #logger.debug('after sub_total, get array={0}'.format(l_invoice_size_quantity))
    msg='==Finish All get list={0}'.format(l_invoice_size_quantity)
    msg_list.save_msg(msg)
    return l_invoice_size_quantity,msg_list

def plot_size_quantity_change(l_invoice_size_quantity,style,colour,plot_way):
    line_type=['b-','g-','r-','c-','m-','y-','k-','bo','go','ro','co','mo',
               'yo','ko','bD','gD','rD','cD','mD','yD','kD','b:','g:','r:','c:','m:','y:','k:','b,','g,','r--']
    labels=get_size_list(style)
    for i in range(len(labels),len(l_invoice_size_quantity[0])-3): #make up the size name with '-'
        labels.append('-')
    labels.append('Sub_Total')
    x=[]
    y_l=[]
    quantity_l=np.sum(np.array(l_invoice_size_quantity)[:,1:-1],axis=0) #calculate total quantity for each size
    base_date=l_invoice_size_quantity[0][0]
    plt.figure()
    if plot_way=='I': #by invoice
        for invoice_size_quantity in l_invoice_size_quantity:
            current_date = invoice_size_quantity[0]
            days = (current_date - base_date).days
            x.append(days)
        x_max = x[-1]
        method=' - By Invoice'

    elif plot_way=='S': #by Season
        x_max = len(l_invoice_size_quantity)
        method=' - By Season'

    y_max=np.array(l_invoice_size_quantity)[:,1:-1].max()
    logger.debug('x_max={0} y_max={1}'.format(x_max,y_max))
    x=np.array(l_invoice_size_quantity)[:,0]
    for i,quantity in enumerate(quantity_l):
        if quantity==0:
            continue
        if labels:
            try:
                label=labels[i]
            except Exception as e:
                logger.error('error when get size label')
                label='None'
        plt.plot(x,np.array(l_invoice_size_quantity)[:,i+1],line_type[i],label=label)
    if plot_way=='I':
        plt.xlabel('Days from {0}'.format(base_date.strftime('%Y-%m-%d')))
    elif plot_way=='S':
        plt.xlabel('Season')

    plt.ylabel('Quantity')
    plt.title('The quantity of each size for {0} - {1} - {2}'.format(style,colour,method))
    plt.legend(loc='upper left')
    #plt.axis(0,x_max,0,y_max)
    #plt.ylim((0,y_max))
    #plt.xlim((0,x_max))
    plt.show()

def get_season_from_date(date):
    month=date.month
    import math
    season='{0}-{1}'.format(date.year,math.ceil(int(month)/3))
    return season

def get_updown_season(current_season):
    c_year,c_season=int(current_season.split('-')[0]),int(current_season.split('-')[1])
    if c_season<4:
        nex_season='{0}-{1}'.format(c_year,c_season+1)
    elif c_season==4:
        nex_season='{0}-{1}'.format(c_year+1,1)
    else:
        logger.error('error when cal next season, wrong season larger than 4')
        return None

    if c_season>1:
        pre_season='{0}-{1}'.format(c_year,c_season-1)
    elif c_season==1:
        pre_season='{0}-{1}'.format(c_year-1,4)
    else:
        logger.error('error when cal next season, wrong season less than 1')
        return None

    return pre_season,nex_season


def get_neighbour_season(current_season,pos):
    c_year, c_season = int(current_season.split('-')[0]), int(current_season.split('-')[1])
    if pos=='NEXT':
        if c_season < 4:
            result_season = '{0}-{1}'.format(c_year, c_season + 1)
        elif c_season == 4:
            result_season = '{0}-{1}'.format(c_year + 1, 1)
        else:
            logger.error('error when cal next season, wrong season larger than 4')
            return None
    else: #Pre season
        if c_season > 1:
            result_season = '{0}-{1}'.format(c_year, c_season - 1)
        elif c_season == 1:
            result_season = '{0}-{1}'.format(c_year - 1, 4)
        else:
            logger.error('error when cal next season, wrong season less than 1')
            return None

    return result_season


def change_to_season(l_invoice_size_quantity):
    #generate all 4 seasons over the years in list
    year_start=l_invoice_size_quantity[0][0].year
    year_end=l_invoice_size_quantity[-1][0].year
    x=[]
    for year in range(year_start,year_end+1):
        for season in range(1,5):
            x.append('{0}-{1}'.format(year,season))
    logger.debug('Got {0} seasons as x {1}'.format(len(x),x))
    #modify all date to season, and set invoice_no. to int(0)
    for i in range(len(l_invoice_size_quantity)):
        season=get_season_from_date(l_invoice_size_quantity[i][0])
        l_invoice_size_quantity[i][0]=season
        l_invoice_size_quantity[i][-1]=0
    #combine to one season one line
    size_name=[]
    for i in range(1,32):
        size_name.append('size{0}'.format(i))

    titles=['season']
    titles.extend(size_name)
    titles.append('invoice_no')
    indexes=np.arange(0,len(l_invoice_size_quantity),1)
    df=pandasDataFrame(data=l_invoice_size_quantity,index=indexes,columns=titles)
    combine_season=df.groupby('season').sum() #sum by same season via Pandas.Datafram
    logger.debug('After combine season , get the dataframe={0}'.format(combine_season))
    tmp_l_invoice_size_quantity=np.array(combine_season,dtype=object) #DataFrame after grouby by, the grouby by column will change to index, so need to add the index to array
    tmp_l_invoice_size_quantity=np.insert(tmp_l_invoice_size_quantity,0,combine_season.index,axis=1)
    #below add allzero to missing season
    last_index=tmp_l_invoice_size_quantity.shape[0]-1 #get last line
    while last_index>0:
        pre_line=tmp_l_invoice_size_quantity[last_index-1] #get pre line of the last line
        nex_season=get_neighbour_season(pre_line[0],'NEXT') #cal next season for pre line
        if nex_season==tmp_l_invoice_size_quantity[last_index][0]: #if calculated next season is current last line, then no gap
            last_index-=1
        else:
            pre_season=get_neighbour_season(tmp_l_invoice_size_quantity[last_index][0],'PRE')
            logger.debug('missing season {0}'.format(pre_season))
            empty_season=[pre_season]
            empty_season.extend((tmp_l_invoice_size_quantity.shape[1]-1)*[0])
            tmp_l_invoice_size_quantity=np.insert(tmp_l_invoice_size_quantity,last_index,empty_season,axis=0)
    logger.debug('After make up missing  season , get the array={0}'.format(tmp_l_invoice_size_quantity))
    return tmp_l_invoice_size_quantity

