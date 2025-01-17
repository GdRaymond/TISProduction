import xdrlib,sys
import xlrd
#from save_db import save
from TISProduction import tis_log
from invoice.common_validate import validate_summary as validate_summary_common
logger=tis_log.get_tis_logger()


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
 'total_quantity':,'total_carton':,'total_gw':,'total_nw':,'total_volume':,'Style':,'style_description':,
 'invoice_no':,'date':,'TISNo':
}
"""


#if the cell given row&col is in the area of size title
def is_size_title(current_row,current_col,upper_row,left_col,right_col):
    if current_row==upper_row+1 and current_col>left_col and current_col<right_col:
        #print("&&&&now it is the size row , current row="+str(current_row))
        return 1
    else:
        return False
    
def str_contain(string,words,all_any='all'):
    result=[str(word).strip().upper() in str(string).strip().upper() for word in words]
    if all_any=='all': #all words must all exist
        return not ( False in result)
    else: #any word exist
        return True in result

"""
Tanhoo has 3 format, 1st:from begining (2010) is Tanhoo's format with Chinese,
 2nd: use TIS, but size will be split to 2 line
 3rd: return to 1st format but cancel chinese
"""
def parse_packing_list_by_TIS(cell_list=[],file='test.xlsx',by_name="RM500BT(TIS16-SO3466)"):
    nrows=len(cell_list)
    ncols=len(cell_list[0])
    packing_list={}
    packing_list["detail"]=[]
    packing_list['summary']={}
    detail_seg=False
    summary_seg=False
    size_list=[]
    summary_list={}
    summary_line={}
    summary_colour=""
    col_from=0
    col_to=1
    col_carton_qty=2
    col_colour_detail=3
    col_per_carton_pcs=14
    col_subtotal=15
    col_per_carton_gw=16
    col_per_carton_nw=17
    col_length=18
    col_width=19
    col_height=20
    col_summary_size=3
    row_size_head=15
    row_summary=50

    """iterate the rows to find the row No. for size head and summary for finding the size title, because in
       Tanhoo document there will be 2 row size title for trousers.
    """
    for rownum in range(nrows):
        current_row=cell_list[rownum]
        if str(current_row[0]).strip().upper()=='FROM' and ('PCS' in [str(item).strip().upper() for item in current_row]):
            row_size_head=rownum
            before_pcs=True
            for colnum in range(ncols):
                current_cell=current_row[colnum]
                if str(current_cell).upper()=="FROM":
                    col_from=colnum
                elif str(current_cell).upper()=="TO":
                    col_to=colnum
                elif str(current_cell).upper()=="" and str_contain(str(cell_list[rownum-1][colnum]),['CTN','QTY']):
                    col_carton_qty=colnum
                elif str_contain(str(current_cell),["DESIGN","COLOR"]):
                    col_colour_detail=colnum
                #below find the 1st size head to get the size_list
                elif colnum>col_colour_detail and before_pcs and (str(current_cell).strip().upper() not in ["","PCS"]):
                    if str(current_cell).strip()=="":
                        continue
                    size_info={}
                    if isinstance(current_cell,float) and float(int(current_cell))==current_cell:
                        size_info["size_name"]=str(int(current_cell)).strip()#for the size like 72.0,16.0,20.0,convert to 72,16,20
                    else:
                        size_info["size_name"]=str(current_cell).strip()#keep 5R, 5.5 
                    size_info["size_col"]=colnum
                    size_list.append(size_info)

                elif str(current_cell).upper()=="PCS" and str_contain(str(cell_list[rownum-1][colnum]),['PER','CARTON']):
                    col_per_carton_pcs=colnum
                    before_pcs=False
                elif str(current_cell).upper()=="PCS" and str_contain(str(cell_list[rownum-1][colnum]),['SUB','TOTAL']):
                    col_subtotal=colnum=colnum

                elif str(current_cell).upper()=="G.W." and str_contain(str(cell_list[rownum-1][colnum]),['PER','CARTON']):
                    col_per_carton_gw=colnum
                elif str(current_cell).upper()=="N.W." and str_contain(str(cell_list[rownum-1][colnum]),['PER','CARTON']):
                    col_per_carton_nw=colnum
                    col_subtotal=colnum
                elif str(current_cell).upper()=="L" and str(cell_list[rownum][colnum-1]).upper()=="N.W.":
                    col_length=colnum
                elif str(current_cell).upper()=="W" and str(cell_list[rownum][colnum-2]).upper()=="N.W.":
                    col_width=colnum
                elif str(current_cell).strip().upper()=="H" and str(cell_list[rownum][colnum-3]).upper()=="N.W.":
                    col_height=colnum
            logger.debug('---col_carton=%s, sizt_list=%s'%(col_carton_qty,size_list))

        elif str_contain(str(current_row[0]).strip().upper(),['PACKING','SUMMARY']):
            row_summary=rownum
            break


    detail_current_colour='' #in the case the colour is omit to follow previous line
    summary_actual_total=0 #some summary has 2 actual shipment, like 1st sea , 2nd sea. We only get the value of last shipment. for the total, we need
                           #to check if it is the last shipment, when we encount the 'BALANCE', it means what in actual qty is the last one, so we can
                           #get this value and accumulate to the summary_actual_total and also write back to summary
    for rownum in range(nrows):
        current_row=cell_list[rownum]
      #  print("==Current row No."+str(rownum)+" : "+str(current_row))

        #find row_size_head to enter the detial_seg
        if rownum==row_size_head:
            detail_seg=True
            summary_seg=False
            continue

        if str(current_row[0]).upper()=="TOTAL":
            detail_seg=False
        
        if detail_seg:
            if str(current_row[col_colour_detail]).strip()=="" and (str(current_row[col_colour_detail+1]).strip()!="" or str(current_row[col_colour_detail+3]).strip()!=""):
                size_list=[]
                for colnum in range(col_colour_detail+1,col_per_carton_pcs):
                    current_cell=current_row[colnum]
                    if str(current_cell).strip()=="":
                        continue
                    size_info={}
                    if isinstance(current_cell,float) and float(int(current_cell))==current_cell:
                        size_info["size_name"]=str(int(current_cell)).strip()#for the size like 72.0,16.0,20.0,convert to 72,16,20
                    else:
                        size_info["size_name"]=str(current_cell).strip() #keep 5R, 5.5 
                    size_info["size_col"]=colnum
                    size_list.append(size_info)
            else:
            #handle the detail carton
                carton_info={}
                try:
                    carton_info['from']=int(float(current_row[col_from]))            
                    carton_info['to']=int(float(current_row[col_to]))
                    carton_info['carton_qty']=int(float(current_row[col_carton_qty]))
                except Exception as err:
                    logger.debug('--%s-%s Get carton No. from=%s, to=%s,qty=%s, error=%s'%(file,by_name,current_row[col_from],current_row[col_to],
                                                                                    current_row[col_carton_qty],err))
                    continue
                try:
                    if current_row[col_colour_detail].strip() not in ['',"‘’",'"']:
                        detail_current_colour=current_row[col_colour_detail].strip().upper()
                        carton_info['colour_detail']=current_row[col_colour_detail].strip().upper()
                        #logger.debug('--%s-%s-current_row[%s]=%s'%(file,by_name,col_colour_detail,current_row[col_colour_detail]))
                    else:
                        carton_info['colour_detail']=detail_current_colour
                        #logger.debug('--%s-%s-detail_current_colour=%s'%(file,by_name,detail_current_colour))
                        
                except Exception as err:
                    logger.error('--%s-%s col_colour_detail=%s current_cell=%s error=%s'\
                                %(file,by_name,current_row[col_colour_detail],current_cell,err))
                carton_info['per_carton_pcs']=current_row[col_per_carton_pcs]
                carton_info['subtotal']=current_row[col_subtotal]
                carton_info['per_carton_gw']=current_row[col_per_carton_gw]
                carton_info['per_carton_nw']=current_row[col_per_carton_nw]
                carton_info['length']=current_row[col_length]
                carton_info['width']=current_row[col_width]
                carton_info['height']=current_row[col_height]
                #logger.error('@@@@@@@the current_row=%s, col_height=%s'%(current_row,col_height))
            
                size_qty={}
                for each_size in size_list:
                    if str(current_row[each_size.get('size_col')]).strip()=="":
                        qty=0
                    else:
                        qty=int(float(str(current_row[each_size.get('size_col')]).strip()))
                    size_qty[each_size.get('size_name')]=qty
                #print('=== in row No.'+str(rownum)+' the size_qty is '+str(size_qty))
                carton_info['size_qty']=size_qty
                if carton_info.get('from')!="":
                    packing_list['detail'].append(carton_info)
            
        if summary_seg:
            #handle the sumary carton
            #below identify the coloumn for summary of each colour
            #Colour Design Size quantity
            if str(current_row[0]).upper().find("DESIGN")!=-1:
                size_list=[] #clear the size_list to be used by summary
                for line in range(1,5):
                    if cell_list[rownum+line][0].strip()!="":
                        summary_colour=cell_list[rownum+line][0].strip().upper()
                        if summary_list.get(summary_colour) is None:
                            summary_list[summary_colour]={}
                            summary_actual_total=0
                for colnum in range(ncols):
                    current_cell=current_row[colnum]
                    if str(current_cell).strip().upper()=="SIZE":
                        col_summary_size=colnum
                    if str(current_cell).strip().upper()=="TOTAL":
                        col_summary_total=colnum
                    if colnum>col_summary_size and str(current_cell).strip().upper()not in ["TOTAL",""]:
                        size_info={}
                        if isinstance(current_cell,float):
                            size_info["size_name"]=str(int(current_cell)).strip() #for the size like 72.0,16.0,20.0,convert to 72,16,20
                        else:
                            size_info["size_name"]=str(current_cell).strip()

                        size_info["size_col"]=colnum
                        size_list.append(size_info)
                logger.debug('\n')
                        
            #when come to Total Quantity, end summary and add summary_list to packing_list            
            elif str(current_row[0]).strip().upper()=='TOTAL QUANTITY': 
                summary_seg=False
                packing_list['summary']=summary_list
                for col in range(1,ncols-1):
                    #logger.debug('*****Total quantity col:%s - %s'%(col,current_row[col]))
                    if str(current_row[col]).strip()!="":
                        packing_list["total_quantity"]=current_row[col]
                        break

            #in the summary line for each colour
            else:
                if str(current_row[col_summary_total]).strip()!="":
                    summary_line=summary_list.get(summary_colour)
                    logger.debug('--%s-%s the  summary_line is sum =%s'%(file,by_name,summary_line))
                    """
                     if the colour is none , like LM16ZF214-SO2617 Hanger, the summary_line is none
                    """
                    if summary_line is None:
                        logger.error('---%s - %s - No colour in summary line  '%(file,by_name))
                        continue 
                    """
                      fix the type of qty line to Order Qty, Actual Qty,Balance,Ratio as the name will change,
                      for example, the 1st Sea Qty should be Actual Qty
                    """
                    qty_type=current_row[col_summary_size]
                    logger.debug('--%s-%s-qty_type is %s,'%(file,by_name,qty_type))
                    if str(qty_type).strip().upper()=='ORDER QTY' or str(qty_type).strip()=='' \
                       and cell_list[rownum-1][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Order Qty'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s-qty_type is %s, the qty_size is%s '%(file,by_name,qty_type,qty_style))
                    elif str(qty_type).strip().upper()=='BALANCE' or str(qty_type).strip()=='' \
                        and cell_list[rownum-3][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Balance'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s-qty_type is %s,the qty_size is%s '%(file,by_name,qty_type,qty_style))
                        summary_actual_total+=summary_line.get('Actual Qty').get('total') #when comes to balance, the last ship qty is actual qty,then sum
                        summary_line['Actual Qty']['total']=summary_actual_total
                        logger.debug('--%s-%s After Balance: the  summary_lin is =%s'%(file,by_name,summary_line))
                    elif str(qty_type).strip().upper()=='RATIO' or str(qty_type).strip()=='' \
                        and cell_list[rownum-4][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Ratio'
                        size_qty={}
                        for each_size in size_list:
                            if summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name'))==0:
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=(summary_line.get('Actual Qty').get('size_qty').get(each_size.get('size_name'))\
                                                                        -summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name')))\
                                                                      /summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name'))                    
                        qty_style={'size_qty':size_qty,'total':current_row[col_summary_total]}
                        logger.debug('--%s-%s--qty_type is %s,the qty_size is%s '%(file,by_name,qty_type,qty_style))
                    elif str_contain(qty_type,['SEA','ACTUAL'],all_any='any') or str(qty_type).strip()=='' \
                        and cell_list[rownum-2][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Actual Qty'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s--qty_type is %s,the qty_size is%s '%(file,by_name,qty_type,qty_style))
                    """in some packinglist, like QPSTO with many size, the summary is split to 2 line
                       for the 1st line, assign the qty_style directly, for the 2nd line need to combine the size and sum the total
                    """
                    logger.debug('--%s-%s summary_actual_total=%s, summary_line[%s]=%s'%(file,by_name,summary_actual_total,qty_type,summary_line.get(qty_type)))
                    if summary_actual_total==0 or summary_line.get(qty_type) is None:
                        summary_line[qty_type]=qty_style   #1st line
                    else: #2nd line
                        combined_size_qty=summary_line.get(qty_type).get('size_qty')
                        logger.debug('--%s-%s before combining the size_qty, the 1st=%s , 2nd=%s'%(file,by_name,combined_size_qty,qty_style.get('size_qty')))
                        combined_size_qty.update(qty_style.get('size_qty'))
                        logger.debug('--%s-%s after combining the size_qty  =%s'%(file,by_name,combined_size_qty))
                        """
                        sum_total=summary_line.get(qty_type).get('total')
                        sum_total+=qty_style.get('total')
                        qty_style['total']=sum_total
                        logger.debug('--%s-%s the  total is sum =%s'%(file,by_name,sum_total))
                        """
                        qty_style['size_qty']=combined_size_qty                    
                        logger.debug('--%s-%s the new qty_style =%s'%(file,by_name,qty_style))
                        summary_line[qty_type]=qty_style
                    summary_list[summary_colour]=summary_line
                    logger.debug('--%s-%s-the summary_list is%s '%(file,by_name,summary_list))


            
        #not in detail_seg or summary_seg
        for colnum in range(ncols):
            current_cell=current_row[colnum]
            if str_contain(current_cell,['packing','summary']):
                row_summary=rownum
                summary_seg=True
            elif str(current_cell).upper().find("PACKAGE")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_carton"]=current_row[col]
                        break
                        
            elif str(current_cell).upper().find("GROSS")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_gw"]=current_row[col]
                        break
                
            elif str(current_cell).upper().find("NET")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_nw"]=current_row[col]
                        break
            elif str(current_cell).upper().find("VOLUME")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_volume"]=current_row[col]
                        break

            elif str(current_cell).strip()=="Style No.":
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["Style"]=str(current_row[col]).strip()
                        break
            elif str(current_cell).strip()=="Description":
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["style_description"]=str(current_row[col]).strip()
                        break
            elif str(current_cell).strip()=="Invoice No.":
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["invoice_no"]=str(current_row[col]).strip()
                        break
            elif str(current_cell).strip().upper().startswith("DATE"):
                for col in range(colnum+1,ncols-1):
                    logger.debug('-%s-%s-read invoice date, col-%s,value-%s'%(file,by_name,col,current_row[col]))
                    if str(current_row[col]).strip()!="":
                        try:
                            packing_list["date"]=xlrd.xldate.xldate_as_datetime(current_row[col],0)
                            break
                        except Exception as err:
                            logger.error('--%s-%s- read date error: %s'%(file,by_name,err))
                            break
            elif str(current_cell).strip()=="Order No.":
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        tmp_str = str(current_row[col]).strip()
                        import re
                        match = re.search('.*(TIS\d{2}-SO\d{4}\w?).*', tmp_str, re.I)
                        if match:
                            packing_list["TISNo"] = match.group(1)
                        else:
                            packing_list["TISNo"] = tmp_str
                        break
                        #packing_list["TISNo"]=str(current_row[col]).strip()
                        #break

    print ('invoice_date=%s,order=%s,style=%s,qty=%s'%(packing_list.get('date'),packing_list.get('TISNo')\
                                                       ,packing_list.get('Style'),packing_list.get('total_quantity')))
    return packing_list

def parse_packing_list(cell_list=[],file='test.xlsx',by_name="RM500BT(TIS16-SO3466)"):
    nrows=len(cell_list)
    ncols=len(cell_list[0])
    packing_list={}
    packing_list["detail"]=[]
    packing_list['summary']={}
    detail_seg=False
    summary_seg=False
    size_list=[]
    summary_list={}
    summary_line={}
    summary_colour=""
    col_from=0
    col_to=1
    col_carton_qty=1
    col_colour_detail=2
    col_per_carton_pcs=14
    col_subtotal=15
    col_per_carton_gw=16
    col_per_carton_nw=17
    col_length=18
    col_width=19
    col_height=20
    col_summary_size=2
    row_size_head=15
    row_summary=50

    """iterate the rows to find the row No. for size head and summary for finding the size title, because in
       Tanhoo document there will be 2 row size title for trousers.
    """
    #print(cell_list)
    for rownum in range(nrows):
        current_row=cell_list[rownum]
        if str(current_row[0]).strip().upper()=='FROM': #TIS format
            logger.debug('-%s-%s-It is TIS template, invoke function parse like Guangzhou module'%(file,by_name))
            return parse_packing_list_by_TIS(cell_list,file,by_name)
        
#        if str(current_row[0]).strip().upper()=='NO.' and ('EACH' in [str(item).strip().upper() for item in current_row]):
#            row_size_head=rownum
        if str(current_row[0]).strip().upper()=='CARTON' and str(current_row[1]).strip().upper()=='CTNS':
            if cell_list[rownum+1][0].strip().upper()=='NO.':
                row_size_head=rownum+1
            else:
                row_size_head=rownum+2
            current_row=cell_list[row_size_head]
            before_each=True
            for colnum in range(ncols):
                current_cell=current_row[colnum]
                #logger.error('--col =%s, cotent=%s'%(colnum,current_cell))

                #if str(current_cell).upper()=="NO." and str(current_row[2]).upper()=='COLOURES':
                if str(current_cell).upper()=="NO." or str(current_cell).upper()=="" and str(cell_list[rownum-2][colnum]).upper()=="CARTON":
                    col_from=colnum
                elif str(current_cell).upper()=="" and cell_list[rownum-2][colnum]=="CTNS":
                    col_carton_qty=colnum
                elif str(current_cell).upper()=="COLOURES":
                    col_colour_detail=colnum
                #below find the 1st size head to get the size_list
                elif colnum>col_colour_detail and before_each and (str(current_cell).strip().upper() not in ["","EACH"]):
                    if str(current_cell).strip()=="":
                        continue
                    size_info={}
                    if isinstance(current_cell,float) and float(int(current_cell))==current_cell:
                        size_info["size_name"]=str(int(current_cell)).strip()#for the size like 72.0,16.0,20.0,convert to 72,16,20
                    else:
                        size_info["size_name"]=str(current_cell).strip()#keep 5R, 5.5 
                    size_info["size_col"]=colnum
                    size_list.append(size_info)

                elif str(current_cell).upper()=="EACH":
                    col_per_carton_pcs=colnum
                    before_each=False
                elif str(current_cell).upper()=="KGS" and str(cell_list[row_size_head][colnum-1]).upper()=="TOTAL":
                    col_per_carton_gw=colnum
                elif str(current_cell).upper()=="KGS" and str(cell_list[row_size_head][colnum-2]).upper()=="TOTAL":
                    col_per_carton_nw=colnum
                elif str(current_cell).upper()=="TOTAL" and str(cell_list[row_size_head][colnum-1]).upper()=="EACH":
                    col_subtotal=colnum
                elif str(current_cell).upper()=="L" and str(cell_list[row_size_head][colnum-1]).upper()=="KGS":
                    col_length=colnum
                elif str(current_cell).upper()=="W" and str(cell_list[row_size_head][colnum-2]).upper()=="KGS":
                    col_width=colnum
                elif str(current_cell).strip().upper()=="H" and str(cell_list[row_size_head][colnum-3]).upper()=="KGS":
                    col_height=colnum
                    #logger.error('--col =%s, height=%s, cotent=%s'%(colnum,col_height,current_cell))

            logger.debug('---col_form=%s,col_carton=%s, sizt_list=%s, Height=%s'%(col_from,col_carton_qty,size_list,col_height))

        elif str_contain(str(current_row[0]).strip().upper(),['COLOR','DESIGN']):
            row_summary=rownum
            break
    

    summary_actual_total=0 #some summary has 2 actual shipment, like 1st sea , 2nd sea. We only get the value of last shipment. for the total, we need
                           #to check if it is the last shipment, when we encount the 'BALANCE', it means what in actual qty is the last one, so we can
                           #get this value and accumulate to the summary_actual_total and also write back to summary
    for rownum in range(nrows):
        current_row=cell_list[rownum]
        logger.debug("==Current row No."+str(rownum)+" : "+str(current_row))
        #if by_name=='10237' and current_row==16:
         #   logger.debug('debug UU77')

        #find row_size_head to enter the detial_seg
        if rownum==row_size_head:
            detail_seg=True
            summary_seg=False
            continue
        
        if str_contain(str(current_row[0]).upper(),['COLOR','DESIGN']):
            detail_seg=False
            summary_seg=True
        
        #in detail_seg
        if detail_seg:
            #check if 2nd row size head
            if str(current_row[col_colour_detail]).strip()=="" and (str(current_row[col_colour_detail+1]).strip()!="" or str(current_row[col_colour_detail+3]).strip()!=""):
                size_list=[]
                for colnum in range(col_colour_detail+1,col_per_carton_pcs):
                    current_cell=current_row[colnum]
                    if str(current_cell).strip()=="":
                        continue
                    size_info={}
                    if isinstance(current_cell,float) and float(int(current_cell))==current_cell:
                        size_info["size_name"]=str(int(current_cell)).strip()#for the size like 72.0,16.0,20.0,convert to 72,16,20
                    else:
                        size_info["size_name"]=str(current_cell).strip() #keep 5R, 5.5 
                    size_info["size_col"]=colnum
                    size_list.append(size_info)

            #handle the detail carton
            else: 
                    if str(current_row[col_from]).strip()=='':
                        continue
                    carton_info={}
                    from_to=str(current_row[col_from]).split('-')
                    
                    try:
                        carton_info['from']=int(float(from_to[0]))
                    except Exception as err:
                        logger.info("--%s-%s from_to=%s, maybe at the line of detail total, error=%s"%(file,by_name,from_to,err))
                        continue
                    if len(from_to)==2: #normal more than 1 carton
                        carton_info['to']=int(float(from_to[1]))
                    elif len(from_to)==1: #only 1 carton
                        carton_info['to']=int(float(from_to[0]))
                    else: #sometimes, it is 1--2
                        for index in range(1,len(from_to)):
                            if from_to[index]!='':
                                carton_info['to']=int(float(from_to[index]))
                                break
                    carton_info['carton_qty']=int(float(current_row[col_carton_qty]))
                    try:
                        if current_row[col_colour_detail].strip() not in ['',"‘’",'"']:
                            detail_current_colour=current_row[col_colour_detail].strip().upper()
                            carton_info['colour_detail']=current_row[col_colour_detail].strip().upper()
                            #logger.debug('--%s-%s-current_row[%s]=%s'%(file,by_name,col_colour_detail,current_row[col_colour_detail]))
                        else:
                            carton_info['colour_detail']=detail_current_colour
                            #logger.debug('--%s-%s-detail_current_colour=%s'%(file,by_name,detail_current_colour))
                        
                    except Exception as err:
                        logger.error('--%s-%s col_colour_detail=%s current_cell=%s error=%s'\
                                        %(file,by_name,current_row[col_colour_detail],err))
                    carton_info['per_carton_pcs']=current_row[col_per_carton_pcs]
                    carton_info['subtotal']=current_row[col_subtotal]
                    carton_info['per_carton_gw']=current_row[col_per_carton_gw]
                    carton_info['per_carton_nw']=current_row[col_per_carton_nw]
                    carton_info['length']=current_row[col_length]
                    carton_info['width']=current_row[col_width]
                    carton_info['height']=current_row[col_height]
                    
                    size_qty={}
                    for each_size in size_list:
                        if str(current_row[each_size.get('size_col')]).strip()=="":
                            qty=0
                        else:
                            qty=int(float(str(current_row[each_size.get('size_col')]).strip()))
                        size_qty[each_size.get('size_name')]=qty
                    #print('=== in row No.'+str(rownum)+' the size_qty is '+str(size_qty))
                    carton_info['size_qty']=size_qty
                    if carton_info.get('from')!="":
                        packing_list['detail'].append(carton_info)
            
        if summary_seg:
            #handle the sumary carton
            #below identify the coloumn for summary of each colour
            #Colour Design Size quantity
            if str(current_row[0]).upper().find("DESIGN")!=-1:
                logger.debug('-%s-%s-Start to parse summary'%(file,by_name))
                size_list=[] #clear the size_list to be used by summary
                for line in range(1,5):
                    if cell_list[rownum+line][0].strip()!="":
                        summary_colour=cell_list[rownum+line][0].strip().upper()
                        if summary_list.get(summary_colour) is None:
                            summary_list[summary_colour]={}
                            summary_actual_total=0
                for colnum in range(ncols):
                    current_cell=current_row[colnum]
                    if str(current_cell).strip().upper()=="SIZE":
                        col_summary_size=colnum
                    if str(current_cell).strip().upper()=="TOTAL":
                        col_summary_total=colnum
                    if colnum>col_summary_size and str(current_cell).strip().upper()not in ["TOTAL",""]:
                        size_info={}
                        if isinstance(current_cell,float) and float(int(current_cell))==current_cell:
                            size_info["size_name"]=str(int(current_cell)).strip() #for the size like 72.0,16.0,20.0,convert to 72,16,20
                        else:
                            size_info["size_name"]=str(current_cell).strip() #keep 5R , 5.5

                        size_info["size_col"]=colnum
                        size_list.append(size_info)
                logger.debug('--%s-%s-the size list is%s '%(file,by_name,size_list))
                        
            #when come to Total Quantity, end summary and add summary_list to packing_list            
            elif str_contain(str(current_row[0]),['TOTAL','QUANTITY']): 
                summary_seg=False
                packing_list['summary']=summary_list
                for col in range(1,ncols-1):
                    #logger.debug('*****Total quantity col:%s - %s'%(col,current_row[col]))
                    if str(current_row[col]).strip()!="":
                        packing_list["total_quantity"]=current_row[col]
                        logger.debug('--%s-%s-the total quantity is%s '%(file,by_name,current_row[col]))
                        break

            #in the summary line for each colour
            else:

                if str(current_row[col_summary_total]).strip()!="":
                    summary_line=summary_list.get(summary_colour)
                    """
                     if the colour is none , like LM16ZF214-SO2617 Hanger, the summary_line is none
                    """
                    if summary_line is None:
                        logger.error('---%s - %s - No colour in summary line  '%(file,by_name))
                        continue 
                    """
                      fix the type of qty line to Order Qty, Actual Qty,Balance,Ratio as the name will change,
                      for example, the 1st Sea Qty should be Actual Qty
                    """
                    qty_type=current_row[col_summary_size]
                    if str(qty_type).strip().upper()=='ORDER QTY' or str(qty_type).strip()=='' \
                       and cell_list[rownum-1][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Order Qty'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s-the qty_size is%s '%(file,by_name,qty_style))

                    elif str(qty_type).strip().upper()=='BALANCE' or str(qty_type).strip()=='' \
                        and cell_list[rownum-3][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Balance'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s-the qty_size is%s '%(file,by_name,qty_style))

                        logger.debug('--%s-%s the  summary_line is sum =%s'%(file,by_name,summary_line))
                        summary_actual_total+=summary_line.get('Actual Qty').get('total') #when comes to balance, the last ship qty is actual qty,then sum
                        summary_line['Actual Qty']['total']=summary_actual_total
                        logger.debug('--%s-%s the  summary_lin is =%s'%(file,by_name,summary_line))
                    elif str(qty_type).strip().upper()=='RATIO' or str(qty_type).strip()=='' \
                        and cell_list[rownum-4][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Ratio'
                        size_qty={}
                        for each_size in size_list:
                            if summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name'))==0:
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=(summary_line.get('Actual Qty').get('size_qty').get(each_size.get('size_name'))\
                                                                      -summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name')))\
                                                                      /summary_line.get('Order Qty').get('size_qty').get(each_size.get('size_name'))                    
                        qty_style={'size_qty':size_qty,'total':current_row[col_summary_total]}
                        logger.debug('--%s-%s-the qty_size is%s '%(file,by_name,qty_style))
                    elif str_contain(qty_type,['SEA','ACTUAL'],all_any='any') or str(qty_type).strip()=='' \
                        and cell_list[rownum-2][col_summary_size].strip().upper()=='SIZE':
                        qty_type='Actual Qty'
                        size_qty={}
                        for each_size in size_list:
                            if str(current_row[each_size.get('size_col')]).strip()=="":
                                size_qty[each_size.get('size_name')]=0
                            else:
                                size_qty[each_size.get('size_name')]=int(float(str(current_row[each_size.get('size_col')]).strip()))                    
                        qty_style={'size_qty':size_qty,'total':int(float(str(current_row[col_summary_total]).strip()))}
                        logger.debug('--%s-%s-the qty_size is%s '%(file,by_name,qty_style))
                    """in some packinglist, like QPSTO with many size, the summary is split to 2 line
                       for the 1st line, assign the qty_style directly, for the 2nd line need to combine the size and sum the total
                    """
                    if summary_actual_total==0 or summary_line.get(qty_type) is None:
                        summary_line[qty_type]=qty_style   #1st line
                    else: #2nd line
                        combined_size_qty=summary_line.get(qty_type).get('size_qty')
                        logger.debug('--%s-%s before combining the size_qty, the 1st=%s , 2nd=%s'%(file,by_name,combined_size_qty,qty_style.get('size_qty')))
                        combined_size_qty.update(qty_style.get('size_qty'))
                        logger.debug('--%s-%s after combining the size_qty  =%s'%(file,by_name,combined_size_qty))
                        """
                        sum_total=summary_line.get(qty_type).get('total')
                        sum_total+=qty_style.get('total')
                        qty_style['total']=sum_total
                        logger.debug('--%s-%s the  total is sum =%s'%(file,by_name,sum_total))
                        """
                        qty_style['size_qty']=combined_size_qty                    
                        logger.debug('--%s-%s the new qty_style =%s'%(file,by_name,qty_style))
                        summary_line[qty_type]=qty_style
                    summary_list[summary_colour]=summary_line
                    logger.debug('--%s-%s-the summary_list is%s '%(file,by_name,summary_list))
            
        #not in detail_seg or summary_seg
        for colnum in range(ncols):
            current_cell=current_row[colnum]
            if str_contain(current_cell,['PACKING','IN']):
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_carton"]=current_row[col]
                        break
                        
            elif str(current_cell).upper().find("GROSS")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_gw"]=current_row[col]
                        break
                
            elif str(current_cell).upper().find("NET")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_nw"]=current_row[col]
                        break
            elif str(current_cell).upper().find("MEASUREMENT")!=-1:
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["total_volume"]=current_row[col]
                        break

            elif str_contain(str(current_cell),["STYLE","NO."]):
                if str(cell_list[rownum-1][colnum]).strip()=='':#the value of style No. will be in merged cell with up cell
                    for col in range(colnum+1,colnum+5):
                        if str(cell_list[rownum-1][col]).strip()!="":
                            packing_list["Style"]=str(cell_list[rownum-1][col]).strip()
                            break
                if packing_list.get("Style") is None:
                    for col in range(colnum+1,colnum+5):
                        if str(current_row[col]).strip()!="":
                            packing_list["Style"]=str(current_row[col]).strip()
                            break

            elif str_contain(str(current_cell),["DESCRIPTION"]):
                if str(cell_list[rownum-1][colnum]).strip()=='':#the value of style No. will be in merged cell with up cell
                    for col in range(colnum+1,colnum+5):
                        if str(cell_list[rownum-1][col]).strip()!="":
                            packing_list["style_description"]=str(cell_list[rownum-1][col]).strip()
                            break
                if packing_list.get("style_description") is None:
                    for col in range(colnum+1,colnum+5):
                        if str(current_row[col]).strip()!="":
                            packing_list["style_description"]=str(current_row[col]).strip()
                            break

            elif str_contain(str(current_cell),["INVOICE","NO."]) or str_contain(str(current_cell),["INVOIVE","NO."]) or str_contain(str(current_cell),["INV","NO."]) or str_contain(str(current_cell),["INY","NO."]) or str_contain(str(current_cell),["INVOICE","NO"]):
                for col in range(colnum+1,ncols-1):
                    if str(current_row[col]).strip()!="":
                        packing_list["invoice_no"]=str(current_row[col]).strip()
                        break
            elif str(current_cell).strip().upper().startswith("DATE"):
                for col in range(colnum+1,ncols-1):
                    logger.debug('-%s-%s-read invoice date, type-%s,col-%s,value-%s'\
                                 %(file,by_name,type(current_row[col]),col,current_row[col]))
                    try:
                        if str(current_row[col]).strip() != "":
                            if type(current_row[col]) is float:
                                packing_list["date"] = xlrd.xldate.xldate_as_datetime(current_row[col], 0)
                            else:
                                packing_list["date"] = current_row[col]
                            break
                    except Exception as e:
                        logger.error('error when checking invoice_date col={0}: {1}'.format(col,e))
                        continue

            elif str_contain(str(current_cell),["ORDER","NO."]):
                if packing_list.get('Style')=='SESOU':
                    logger.debug('start debug SESOU')
                if str(cell_list[rownum-1][colnum]).strip()=='':#the value of style No. will be in merged cell with up cell
                    for col in range(colnum+1,colnum+5):
                        if str(cell_list[rownum-1][col]).strip()!="":
                            tmp_str=str(cell_list[rownum-1][col]).upper().strip()
                            import re
                            match=re.search('.*(TIS\d{2}-S[O0]\d{4}\w?).*',tmp_str,re.I)
                            if match:
                                packing_list["TISNo"]=match.group(1)
                            else:
                                packing_list["TISNo"] =tmp_str
                            break
                if packing_list.get("TISNo") is None:
                    for col in range(colnum+1,colnum+5):
                        if str(current_row[col]).strip()!="":
                            tmp_str=str(current_row[col]).upper().strip()
                            import re
                            match = re.search('.*(TIS\d{2}-S[O0]\d{4}\w?).*', tmp_str, re.I)
                            if match:
                                packing_list["TISNo"] = match.group(1)
                            else:
                                packing_list["TISNo"] = tmp_str
                            break

    #print(packing_list)
    print ('invoice_date=%s,order=%s,style=%s,qty=%s'%(packing_list.get('date'),packing_list.get('TISNo')\
                                                       ,packing_list.get('Style'),packing_list.get('total_quantity')))
    if not packing_list.get('invoice_no',None):
        logger.error('!!!!!!Can not find the invoice no for order {0} - style {1} in {2} - {3} '.format(
            packing_list.get('TISNo'),packing_list.get('Style'),file,by_name
        ))
    if len(packing_list.get('TISNo'))>=12: #for the order No. use S0(zero) instead of SO, change 0 to O
        packing_list['TISNo']=packing_list['TISNo'][:7]+'O'+packing_list['TISNo'][8:]
    else:
        logger.error('!!!!! Can not get corret the TISNo {0}  for  style {1} in {2} - {3} '.format(
            packing_list.get('TISNo'),packing_list.get('Style'),file,by_name
        ))

    return packing_list

"""from detail to calculate the summary
   return: summary_by_cal={'-Cobalt blue':{'total':, 'size_qty'{'-2xs':,...}},
                           ...
                          }
"""
def calculate_detail(packing_list={},file='test.xlsx',by_name="RM500BT(TIS16-SO3466)"):
    logger.debug('======================================')
    logger.debug('Start calculate_detail and validate detail')
    detail_correct = True
    summary_by_cal={}  #init the result dict
    list_carton_no_from=[]
    list_carton_no_to=[]
    carton_total_by_cal=0

    logger.debug('-Start  validate carton No. in each line')
    all_correct=True
    for line in packing_list.get('detail'):
        #validate the carton No. and quantity
        carton_no_from=line.get('from')
        carton_no_to=line.get('to')
        carton_line_total=line.get('carton_qty')
        if  carton_line_total!=(carton_no_to-carton_no_from+1):
            logger.error('--%s - %s - Carton No. wrong at line from:%s to:%s total:%s '%(file,by_name,carton_no_from,carton_no_to,carton_line_total))
            all_correct=False       
        
        #put the carton no to list and accumulate the carton qty
        list_carton_no_from.append(carton_no_from)
        list_carton_no_to.append(carton_no_to)
        carton_total_by_cal+=carton_line_total
        
        colour=line.get('colour_detail')
        temp_dict=summary_by_cal.get(colour)
        if temp_dict is None:
            temp_dict={}
        temp_size_qty=temp_dict.get('size_qty')
        if temp_size_qty is None:
            temp_size_qty={}
        for size in line.get('size_qty'):
            #print("====in colour=%s, size=%s , carton qty=%s, per carton=%s "%(colour,size,line.get('to')-line.get('from')+1,line.get('size_qty').get(size)))
            base_qty=temp_size_qty.get(size)
            if base_qty is None:
                base_qty=0
            try:
                temp_size_qty[size]=base_qty+ carton_line_total*line.get('size_qty').get(size)
            except Exception as err:
                logger.error('--%s - %s - detail line cal error at from=%s to=%s. base_qty=%s, carton_line_total=%s,size_qty[%s]=%s'
                             %(file,by_name,carton_no_from,carton_no_to,base_qty,carton_line_total,size,line.get('size_qty').get(size)))
        temp_dict['size_qty']=temp_size_qty
        temp_dict['total']=0
        summary_by_cal[colour]=temp_dict
    if all_correct:
        logger.debug('--Correct of carton No. in each line ')
    else:
        detail_correct=False


    # validate the consistency of no. and quantity by iterate\ing the carton no list
    all_correct=True
    logger.debug('-Start validate the consistency of carton no.')
    for no in range(0,len(list_carton_no_from)-1):
        if float(list_carton_no_from[no+1])!=float(list_carton_no_to[no])+1:
            all_correct=False
            logger.error('--%s - %s - Carton No. not consistant at line to:%s next from:%s  '\
                         %(file,by_name,list_carton_no_to[no],list_carton_no_from[no+1]))
    if all_correct:
        logger.debug('--Correct of the consistency of carton No. ')
    else:
        detail_correct=False

    if detail_correct:
        logger.debug('-Correct detail carton No.')
        
    # validate the carton quantity 
    logger.debug('========================================')
    logger.debug('Start validate the total carton quantity')
    if carton_total_by_cal==packing_list.get('total_carton'):
        logger.debug('-Correct of he total carton quantity.')
    else:
        logger.error('-%s-%s-Wrong of the total carton, in sheet - %s, but by calculation - %s'\
                     %(file,by_name,packing_list.get('total_carton'),carton_total_by_cal))

    for item in summary_by_cal:
        temp_dict=summary_by_cal.get(item)
        temp_total=temp_dict.get('total')
        for size in temp_dict.get('size_qty'):
            temp_total+=temp_dict.get('size_qty').get(size)
        temp_dict['total']=temp_total
        summary_by_cal[item]=temp_dict
    return summary_by_cal

#validate the summary with detail
def validate_summary(packing_list={},file='test.xlsx',by_name="RM500BT(TIS16-SO3466)"):
    #calculate detail
    detail=calculate_detail(packing_list=packing_list,file=file,by_name=by_name)

    all_summary_correct=True
    logger.debug('======================================')
    logger.debug('Start validate summary')
    #validate sumary on ratio and balance
    value_summary=packing_list.get('summary')
    l_msg_success=[]
    msg='\nStart verify {0} {1}'.format(file,by_name)
    l_msg_success.append(msg)
    l_msg_error=[]
    for colour in value_summary:     
        value_colour=value_summary.get(colour)
        
        #validate the ratio, find the ration greater than 5% and balance greater than 10pcs
        logger.debug('-Start validate the ratio for colour:%s , checking if ratio> %%5 and balance>10pcs'%(colour))
        all_correct=True
        try:            
            ratio=value_colour.get('Ratio').get('size_qty')
            balance=value_colour.get('Balance').get('size_qty')
        except Exception as err:
            msg='--%s - %s - Ratio or balance can not find, error--%s'\
                             %(file,by_name,err)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        balance_by_cal=0
        for size in ratio:
            ratio_value=ratio.get(size)
            balance_value=balance.get(size)
            balance_by_cal+=balance_value
            #logger.debug('size:%s--ratio:%s'%(size,ratio_value))
            if str(ratio_value).strip()!="" and ratio_value>0.05 \
               and str(balance_value).strip()!="" and balance_value>9:
                msg='--%s - %s - Ratio warning at colour:%s size:%s - ratio: %s, balance:%s'\
                             %(file,by_name,colour,size,ratio_value,balance_value)
                logger.error(msg)
                l_msg_error.append(msg)
                all_correct=False
        if balance_by_cal!=value_colour.get('Balance').get('total'):
            msg='--%s-%s - Balance total is not correct at colour: %s, in doc=%s, cal=%s'\
                         %(file,by_name,colour,value_colour.get('Balance').get('total'),balance_by_cal)
            logger.error(msg)
            l_msg_error.append(msg)
            all_correct=False
        if all_correct:
            msg='--The total balance is correct and  ratio for colour: %s is ok without exceeding 5%% and balance greater than 10pcs'%colour
            logger.debug(msg)
            l_msg_success.append(msg)
        else:
            all_summary_correct=False

    #validate summary the quantity  comparing with detail quantity : 1- colour from summary to detail
    logger.debug('-Start validate the quantity for colour:, summary-> detail')
    summary_correct=True
    summary_total_qty=0
    for colour in value_summary:
        logger.debug('--Start validate the quantity for colour:%s, summary-> detail'%colour)
        all_correct=True
        value_colour=value_summary.get(colour)

        """
          if the Actual Qty name is varied, like LM17ZF202-ob-sox, the name is BY SEA, then error here
        if by_name=='RM301EWS(TIS15-SO3127)':
            logger.error('RM301EWS(TIS15-SO3127)--value_colour %s'%value_colour)
        """
        

        try:   
            actual_qty=value_colour.get('Actual Qty')
            summary_total_qty+=actual_qty.get('total')
            actual_qty_size_qty=actual_qty.get('size_qty')
        except Exception as e:
            msg='---%s - %s - Can not find Actual Qty name: %s'%(file,by_name,e)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        """
          if the colour name in detail not consistant with summary, error will occur
          for example, in LM16ZF214-SO3469, coulur in detail is INK, in summary is INK NAVY
        """
        if detail.get(colour) is None:
            msg='---%s - %s - Can not find colour:%s in detail '\
                             %(file,by_name,colour)
            logger.error(msg)
            l_msg_error.append()
            continue
        detail_size_qty=detail.get(colour).get('size_qty')
        #validate the actural qty , 1.1 - size from summary to detail
        total_by_cal=0
        for size in actual_qty_size_qty:
            actual_qty_size_qty_value=actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip()!="":
               # logger.debug('---%s - %s - Qty data at colour:%s size:%s - size qty: %s, temp total:%s'\
                           #  %(file,by_name,colour,size,actual_qty_size_qty_value,total_by_cal))
                total_by_cal+=actual_qty_size_qty_value

                if actual_qty_size_qty_value!=detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size)==0) or \
                       (actual_qty_size_qty_value==0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg='---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s'\
                             %(file,by_name,colour,size,actual_qty_size_qty_value,detail_size_qty.get(size))
                    logger.error(msg+' Colour:sum->detai size:sum->detal')
                    l_msg_error.append(msg)
                    all_correct=False
                    summary_correct=False
        
        #validate the actual qty total, comparing with calculation
        if actual_qty.get('total')!=total_by_cal:
            msg='---%s - %s - Actual qty total warning at colour:%s  - in doc: %s, by calculation:%s'\
                        %(file,by_name,colour,actual_qty.get('total'),total_by_cal)
            logger.error(msg)
            l_msg_error.append(msg)

        
        #validate the actural qty , 1.2 - size from detail to summary
        for size in detail_size_qty:
            actual_qty_size_qty_value=actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip()!="":
                if actual_qty_size_qty_value!=detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size)==0) or \
                       (actual_qty_size_qty_value==0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg='---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s'\
                             %(file,by_name,colour,size,actual_qty_size_qty_value,detail_size_qty.get(size))
                    logger.error(msg+' Colour:sum->detai size:detail->sum')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct=False
                    summary_correct=False

        if all_correct:
            msg='---Correct: the quantity for colour:%s, summary-> detail '%colour
            logger.debug(msg)
            l_msg_success.append(msg)
    if summary_correct:
        msg='--All Correct: the quantity colour summary-> detail '
        logger.debug(msg)
        l_msg_success.append(msg)
    else:
        all_summary_correct=False
        
        

    #validate summary the quantity  comparing with detail quantity : 2- colour from detail to summary
    logger.debug('-Start validate the quantity for colour, detail-> summary')
    summary_correct=True
    for colour in detail:
        logger.debug('--Start validate the quantity for colour:%s, detail-> summary'%colour)
        all_correct=True
        value_colour=value_summary.get(colour)
        
        """
          if the colour name in detail not consistant with summary, error will occur
          for example, in LM16ZF214-SO3469, coulur in detail is INK, in summary is INK NAVY
        """
        if value_colour is None:
            msg='---%s - %s - Can not find colour:%s in summary '\
                             %(file,by_name,colour)
            logger.error(msg)
            l_msg_error.append(msg)
            continue

        try:
            actual_qty=value_colour.get('Actual Qty')
            actual_qty_size_qty=actual_qty.get('size_qty')
        except Exception as e:
            msg='---%s-%s-Can not find Actural Qty name - %s'%(file,by_name,e)
            logger.error(msg)
            l_msg_error.append(msg)
            continue
        detail_size_qty=detail.get(colour).get('size_qty')
        #validate the actural qty , 2.1 - size from summary to detail
        for size in actual_qty_size_qty:
            actual_qty_size_qty_value=actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip()!="":
                if actual_qty_size_qty_value!=detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size)==0) or \
                       (actual_qty_size_qty_value==0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg='---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s'\
                             %(file,by_name,colour,size,actual_qty_size_qty_value,detail_size_qty.get(size))
                    logger.error(msg+' Colour:detail->sum size:sum->detail')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct=False
                    summary_correct=False
        
        #validate the actural qty , 2.2 - size from detail to summary
        for size in detail_size_qty:
            actual_qty_size_qty_value=actual_qty_size_qty.get(size)
            if str(actual_qty_size_qty_value).strip()!="":
                if actual_qty_size_qty_value!=detail_size_qty.get(size):
                    if ((actual_qty_size_qty_value is None) and detail_size_qty.get(size)==0) or \
                       (actual_qty_size_qty_value==0 and (detail_size_qty.get(size) is None)):
                        continue
                    msg='---%s - %s - Qty warning at colour:%s size:%s - summary: %s, detail:%s'\
                             %(file,by_name,colour,size,actual_qty_size_qty_value,detail_size_qty.get(size))
                    logger.error(msg+' Colour:detail->sum size:detail->sum')
                    if msg not in l_msg_error:
                        l_msg_error.append(msg)
                    all_correct=False
                    summary_correct=False

        if all_correct:
            msg='---Correct: the quantity for colour:%s, detail-> summary '%colour
            logger.debug(msg)
            l_msg_success.append(msg)
    if summary_correct:
        msg='--All Correct: the quantity colour detail-> summary '
        logger.debug(msg)
        l_msg_success.append(msg)
    else:
        all_summary_correct=False
        
    #validate total quantity in doc comparing with sum of each colour in summary
    logger.debug('-Start validate total quantity ')
    if packing_list.get('total_quantity')!=summary_total_qty:
        msg='--%s - %s -Validate total quantity Wrong: in doc:%s - sum  in summary %s '\
                     %(file,by_name,packing_list.get('total_quantity'),summary_total_qty)
        logger.error(msg)
        l_msg_error.append(msg)
        all_summary_correct=False

    else:
        msg='--Validate total quantity Correct'
        logger.debug(msg)
        l_msg_success.append(msg)

    if all_summary_correct:
        msg='-All correct of summary'
        logger.debug(msg)
        l_msg_success.append(msg)

    #return all_summary_correct
    result={'msg_success':l_msg_success,'msg_error':l_msg_error,'total_carton':packing_list.get('total_carton')}
    return result

"""

"""
def validate_packinglist_by_sheet(cell_list=[],filename='',sheetname='',save_db=False):
    packing_list=parse_packing_list(cell_list=cell_list,file=filename,by_name=sheetname)
    verify_result=validate_summary_common(packing_list=packing_list,file=filename,by_name=sheetname)
    #if save_db==True:
        #count=save(packing_list=packing_list,fty='TH',file=filename,by_name=sheetname)
    result={'verify':verify_result,'packing_list':packing_list}

    return result
        

    
