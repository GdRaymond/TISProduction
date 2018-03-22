import sys
from TISDesk.mainwindow import TISMainWindow
from PyQt5.QtWidgets import QApplication
from TISProduction import tis_log

if __name__=="__main__":
    tis_log.init_tis_logger()
    app=QApplication(sys.argv)
    mainwindow=TISMainWindow()
    mainwindow.show()
    sys.exit(app.exec_())