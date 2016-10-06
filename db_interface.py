__author__ = 'aschwartz - Schwartz210@gmail.com'
from sqlite3 import connect
DATABASE = 'test.db'
tables = {'contacts' :'test_table4',
          'sales' : 'sales5'}

fields_type_mapping = {'ID' : 'contacts',
                       'First_name' : 'contacts',
                       'Last_name' : 'contacts',
                       'Address1' : 'contacts',
                       'Address2' : 'contacts',
                       'City' : 'contacts',
                       'State' : 'contacts',
                       'Zip' : 'contacts',
                       'Phone' : 'contacts',
                       'Order_num' : 'sales',
                       'Customer_ID' : 'sales',
                       'Amount' : 'sales',
                       'Order_date' : 'sales'}

def flexible_SQL(get_fields, table, **kwargs):
    '''
    Returns a SQL_request(string). Supports 'WHERE' and 'ORDER BY' statements.
    '''
    SQL_request =  'SELECT %s FROM %s' % (get_fields, tables[table])
    if kwargs['where']:
        where_field, criteria = kwargs['where']
        SQL_request += ' WHERE %s="%s"' % (where_field, criteria)
    if 'order_by' in kwargs and kwargs['order_by']:
        order_by_field, order = kwargs['order_by']
        SQL_request += ' ORDER BY %s %s' % (order_by_field, order)
    return SQL_request

def query_sum(total_by, field, criteria):
    table = fields_type_mapping[total_by]
    sql_request = 'SELECT SUM(%s) FROM %s WHERE %s="%s"' % (total_by, tables[table], field, criteria)
    total = pull_data(sql_request)[0][0]
    if total:
        return total
    else:
        return 0.00

def create_table(table):
    if table == 'contacts':
        sql_request = 'CREATE TABLE %s(ID INTEGER PRIMARY KEY AUTOINCREMENT, First_name, Last_name, Address1, Address2, City, State, Zip, Phone)' % (tables[table])
    elif table == 'sales':
        sql_request = 'CREATE TABLE %s (Order_num INTEGER PRIMARY KEY AUTOINCREMENT, Customer_ID, Amount Decimal(19,2), Order_date DATE)' % (tables[table])
    else:
        raise Exception('Unknown table')
    execute_sql(sql_request)

def execute_sql(SQL_request):
    '''
    Alter database. Does not query data.
    '''
    conn = connect(DATABASE)
    c = conn.cursor()
    c.execute(SQL_request)
    conn.commit()
    conn.close()

def execute_multiple_sql(SQL_requests):
    conn = connect(DATABASE)
    c = conn.cursor()
    for SQL_request in SQL_requests:
        c.execute(SQL_request)
    conn.commit()
    conn.close()

def exists(sql_request):
    '''
    Evualuate if record exists. Returns boolean.
    '''
    conn = connect(DATABASE)
    c = conn.cursor()
    count = len(list(c.execute(sql_request)))
    if count > 0:
        out = True
    else:
        out = False
    conn.commit()
    conn.close()
    return out

def pull_data(SQL_request):
    '''
    Inputs SQL_request, outputs records
    '''
    conn = connect(DATABASE)
    c = conn.cursor()
    try:
        list_of_tuples = list(c.execute(SQL_request))
        list_of_lists = [list(elem) for elem in list_of_tuples]
        conn.commit()
        conn.close()
        return list_of_lists
    except:
        raise Exception('Not able to fulfill request')

def add_record(table, record):
    if table == 'contacts':
        sql_request = 'INSERT INTO %s VALUES(NULL, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (tables[table], record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7])
    elif table == 'sales':
        sql_request = 'INSERT INTO %s VALUES(NULL, "%s", %s, "%s")' % (tables[table], record[0], record[1], record[2])
    else:
        raise Exception()
    execute_sql(sql_request)

def update_record(table, values):
    if table == 'contacts':
        sql_request = 'UPDATE %s SET First_name="%s", Last_name="%s", Address1="%s", Address2="%s", City="%s", ' \
                      'State="%s", Zip="%s", Phone="%s" WHERE ID="%s"' % (tables[table],
                                                                          values[0],
                                                                          values[1],
                                                                          values[2],
                                                                          values[3],
                                                                          values[4],
                                                                          values[5],
                                                                          values[6],
                                                                          values[7],
                                                                          values[8])
    elif table == 'sales':
        sql_request = 'UPDATE %s SET Customer_ID="%s", Amount=%s, Order_date="%s" WHERE ID="%s"' % (tables[table], values[0], values[1], values[2],values[3])
    else:
        raise Exception()
    execute_sql(sql_request)

def field_name(field):
    table = fields_type_mapping[field]
    sql_table_name = tables[table]
    name =  sql_table_name + '.' + field
    return name

def delete_where(table, field, criteria):
    sql_request = 'DELETE FROM %s WHERE %s="%s"' % (tables[table], field, criteria)
    execute_sql(sql_request)


sales_report1 = 'SELECT test_table4.First_name, test_table4.Address1, sales2.Amount FROM sales2 INNER JOIN test_table4 ON sales2.Customer_ID=test_table4.ID'

sales_sample_data = [
    [12,12.16,'20160928'],
    [10,13.16,'20160822'],
    [2,12.66,'20160823'],
    [4,48.16,'20160707'],
    [6,52.17,'20160628'],
    [5,9.16,'20160228'],
    [11,11.16,'20160815'],
    [9,58.16,'20160928'],
    [3,149.16,'20160905'],
    [12,153.16,'20160928'],
    [4,77.58,'20160427'],
    [6,22.58,'20160428'],
    [8,155.58,'20160429'],
    [10,77.22,'20160401'],
    [12,98.63,'20160402'],
    [14,172.54,'20160403'],
    [16,180.45,'20160404'],
    [15,190.10,'20160405'],
    [13,117.45,'20160406'],
    [11,111.23,'20160407'],
    [9,145.96,'20160408']
]
