from PyQt5.QtWidgets import QDialog
from TISDesk.TIS_edit_dialog import Ui_editDialogShipment
from TISDesk.TIS_edit_order_dialog import Ui_editDialog_Order
from shipments.models import Shipment

class Edit_Dialog_Order(QDialog):
    def __init__(self,parent=None,**kwargs):
        super(Edit_Dialog_Order,self).__init__(parent)
        self.ui=Ui_editDialog_Order()
        self.ui.setupUi(self)
        order_recap1='ID {0} - {1} - {2} - {3} - {4} pcs'.format(kwargs.get('id'),kwargs.get('tis_no')\
                                                    ,kwargs.get('style'),kwargs.get('colour'),kwargs.get('quantity'))
        self.ui.lb_recap_1.setText(order_recap1)
        order_recap2='Made by {0} for client {1}'.format(kwargs.get('supplier'),kwargs.get('client'))
        self.ui.lb_recap_2.setText(order_recap2)
        self.ui.lin_abmno.setText(kwargs.get('abm_no'))
        self.ui.comb_shipment.addItems(kwargs.get('shipments'))
        if kwargs.get('order_date'):
            self.ui.dateE_orderdate.setDate(kwargs.get('order_date'))


class Edit_dialog_shipment(QDialog):
    def __init__(self,parent=None,**kwargs):
        super(Edit_dialog_shipment,self).__init__(parent)
        self.ui=Ui_editDialogShipment()
        self.ui.setupUi(self)
        shipment_recap1='ID {0} - {1} - made by {2}'.format(kwargs.get('id','Nil'),kwargs.get('code','Nil'),kwargs.get('Supplier','Nil'))
        self.ui.lb_recap_1.setText(shipment_recap1)
        shipment_recap2='{0} pcs - {1} cartons {2} m3 - {3} kg '.format(kwargs.get('quantity','Nil'),kwargs.get('carton', 'Nil'),kwargs.get('volume','Nil'),kwargs.get('weight','Nil'))
        self.ui.lb_recap_2.setText(shipment_recap2)
        shipment_recap3='in container {0}'.format(kwargs.get('container','Nil'))
        self.ui.lb_recap_3.setText(shipment_recap3)
        if kwargs.get('etd'):
            self.ui.dateE_etd.setDate(kwargs.get('etd'))
        if kwargs.get('eta'):
            self.ui.dateE_eta.setDate(kwargs.get('eta'))
        if kwargs.get('instore'):
            self.ui.dateE_instore.setDate(kwargs.get('instore'))
        if kwargs.get('instore_abm'):
            self.ui.dateE_instore_abm.setDate(kwargs.get('instore_abm'))
        mode_list=[a[0] for a in list(Shipment.MODE) ]
        self.ui.comb_mode.addItems(mode_list)
        self.ui.comb_mode.setCurrentText(str(kwargs.get('mode')))
        etd_port_list=[a[0] for a in list(Shipment.ETD_PORT)]
        self.ui.comb_etdport.addItems(etd_port_list)
        self.ui.comb_etdport.setCurrentText(str(kwargs.get('etd_port')))
        eta_port_list=[a[0] for a in list(Shipment.ETA_PORT)]
        self.ui.comb_etaport.addItems(eta_port_list)
        self.ui.comb_etaport.setCurrentText(str(kwargs.get('eta_port')))


