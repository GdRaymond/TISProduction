from django.db import connection,transaction
import os
os.environ['DJANGO_SETTINGS_MODULE']='TISProduction.settings'
from TISProduction import tis_log

logger=tis_log.get_tis_logger()

def create_my_search():
    cursor=connection.cursor()
    #CREATE VIRTUAL TABLE my_search using FTS3(slug, body);
    cursor.execute('create virtual table my_search using FTS3(table_name,obj_id,text)')
    transaction.commit()
    logger.debug(' created my_search virtual table')

def clear_my_search():
    cursor=connection.cursor()
    #CREATE VIRTUAL TABLE my_search using FTS3(slug, body);
    cursor.execute('delete from my_search')
    transaction.commit()
    logger.debug(' clear all index in my_search')


def add_index(content):
    '''
    insert the index of FTS to my_search table
    :param content: a list of dict which contain {'table_name':, 'obj_id':,'text':}
    :return:
    '''
    os.environ['DJANGO_SETTINGS_MODULE'] = 'TISProduction.settings'
    cursor = connection.cursor()
    logger.debug(' startging save the index to my_search {0} records'.format(len(content)))
    for line in content:
        table_name=line.get('table_name')
        obj_id=line.get('obj_id')
        text=line.get('text')
        sql_str="insert into my_search values('{0}','{1}','{2}')".format(table_name,obj_id,text)
        logger.debug('  sql_str: {0}'.format(sql_str))
        cursor.execute(sql_str)
    transaction.commit()
    logger.debug(' finished save the index to my_search {0} records'.format(len(content)))

def search_index(key_word):
    '''
    search the my_search table
    :param key_word: str - input by user
    :return: list of dict which contain {'table_name','obj_id'}
    '''
    table_l=[]
    key_word=key_word.replace('-',' ') #when search 'JF-NOV' will get result contain JF OR NOV, when search 'JF NOV', result containt both
    sql_str="select table_name,obj_id from my_search where text match '{0}'".format(key_word)
    logger.debug(' the sql_str is:{0}'.format(sql_str))
    try:
        cursor=connection.cursor()
        cursor.execute(sql_str)
        result=cursor.fetchall() # result:[(table_name,obj_id),()]
    except Exception as e:
        logger.error(' error occur when search: {0}'.format(e))
    logger.debug(' find {0} records in my_search for {1}'.format(len(result),key_word))

    for line in result:
        item={'table_name':line[0],'obj_id':line[1]}
        table_l.append(item)
    logger.debug(' assemble table info to list {0}'.format(table_l))
    return table_l

