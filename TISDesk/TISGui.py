import sys,os
#import django
import django.template.loader_tags
#from django.conf import settings
#from TISProduction import settings as my_default

#sys.path.append('C:\\Users\\rhe\\PyCharm\\TISProduction')  # 将项目路径添加到系统搜寻路径当中
os.environ['DJANGO_SETTINGS_MODULE'] = 'TISProduction.settings'  # 设置项目的配置文件
#settings.configure(default_settings=my_default,DEBUG=True)
django.setup()  # 加载项目配置

from TISDesk.mainwindow import TISMainWindow
from PyQt5.QtWidgets import QApplication
from TISProduction import tis_log

if __name__=="__main__":

    tis_log.init_tis_logger()
    app=QApplication(sys.argv)
    mainwindow=TISMainWindow()
    mainwindow.show()
    sys.exit(app.exec_())