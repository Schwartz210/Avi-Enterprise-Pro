__author__ = 'Avi Schwartz - Schwartz210@gmail.com'
from gui import run
from db_interface import create_table, add_record, DATABASE

def start():
    try:
        open(DATABASE)
        run()
    except:
        installer()


def installer():
    print('Run installer')
    create_table('contacts')
    create_table('sales')
    contact_record = ['Avi','Schwartz','123 Address St', 'Apartment #', 'New York','New York', '11111','845-701-5462']
    add_record('contacts', contact_record)
    sales_record = ['1','0.00','2016-12-31']
    add_record('sales', sales_record)
    print('Installation complete')




start()