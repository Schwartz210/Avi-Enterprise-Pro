__author__ = 'aschwartz - Schwartz210@gmail.com'
from db_interface import add_record, pull_data, update_record, field_name, query_sum, fields_type_mapping, flexible_SQL, delete_where, update_all_cust_totals
from excel import export
from tkinter import *
from functools import partial
from PIL import Image, ImageTk

type_to_fields = {'contacts': ['ID', 'First_name', 'Last_name','Address1', 'Address2','City','State','Zip','Phone', 'Total_sales'],
                  'sales' : ['Order_num', 'Customer_ID', 'Amount', 'Order_date']}

special_id = {'contacts' : 'ID',
              'sales' : 'Order_num'}

def null_entry_handler(entry):
    if len(entry.get()) == 0:
        return ''
    else:
        return entry.get()

class HomeScreen(object):
    '''
    This class is home window. It's the first screen you see when program is initiated. When it's closed, the entire-
    program stops running.
    '''
    def __init__(self):
        self.master = Tk()
        self.layout()
        self.menubar()
        self.master.mainloop()

    def layout(self):
        self.master.title('Avi Enterprise Pro')
        self.master.wm_geometry("600x600")
        self.photo_contact = ImageTk.PhotoImage(Image.open('image/contact.png'))
        self.photo_record = ImageTk.PhotoImage(Image.open('image/record.png'))
        self.photo_sales = ImageTk.PhotoImage(Image.open('image/sales.png'))
        self.button_new_contact = Button(self.master, image=self.photo_contact, borderwidth=0, command=self.new_contact)
        self.button_new_contact.grid(sticky=W, column=0, row=0)
        self.button_record = Button(image=self.photo_record, borderwidth=0, command=self.contacts)
        self.button_record.grid(sticky=W, column=0, row=1)
        self.button_sales = Button(image=self.photo_sales, borderwidth=0, command=self.sales)
        self.button_sales.grid(sticky=W, column=0, row=2)

    def menubar(self):
        self.menu = Menu(self.master)
        #File menu
        filemenu = Menu(self.menu, tearoff=0)
        filemenu.add_command(label="Open", command=self.hello)
        filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        self.menu.add_cascade(label="File", menu=filemenu)
        #Record menu
        recordmenu = Menu(self.menu, tearoff=0)
        recordmenu.add_command(label="New Contact", command=self.new_contact)
        recordmenu.add_command(label="New Sales Order", command=self.new_sales_order)
        recordmenu.add_command(label="Customer Center", command=self.customer_center)
        self.menu.add_cascade(label="Records", menu=recordmenu)
        #Reporting menu
        reportingmenu = Menu(self.menu, tearoff=0)
        reportingmenu.add_command(label="Customer List", command=self.contacts)
        reportingmenu.add_command(label="Sales Orders", command=self.sales)
        reportingmenu.add_command(label="Customer Sales Total", command=self.customer_sales_total)
        self.menu.add_cascade(label="Reporting", menu=reportingmenu)
        self.master.config(menu=self.menu)

    def hello(self):
        pass

    def new_contact(self):
        CreateRecordWindow('contacts')

    def new_sales_order(self):
        CreateRecordWindow('sales')

    def contacts(self):
        fields = list(type_to_fields['contacts'])
        Report('contacts', fields)

    def sales(self):
        fields = list(type_to_fields['sales'])
        Report('sales', fields)

    def customer_center(self):
        fields = ['Last_name', 'First_name', 'Total_sales']
        CustomerCenter('contacts', fields)

    def customer_sales_total(self):
        fields = ['Last_name', 'First_name', 'Total_sales']
        Report('contacts', fields)


class CreateRecordWindow(object):
    '''
    The window is allows the user to create a new contact record.
    '''
    def __init__(self, report_type):
        self.report_type = report_type
        self.master = Toplevel()
        icon = 'image/%s.ico' % (report_type)
        self.master.iconbitmap(icon)
        self.entries = []
        self.layout()

    def layout(self):
        fields = list(type_to_fields[self.report_type])
        spec_id = special_id[self.report_type]
        fields.remove(spec_id)
        titles = {'contacts' : 'New Contact', 'sales' : 'New Sales Order'}
        self.master.title(titles[self.report_type])
        entry_width = 30
        row_num = 1
        for field in fields:
            text = field.replace('_', ' ')
            Label(self.master, text=text).grid(column=1, row=row_num, sticky=W)
            entry = Entry(self.master, width=entry_width)
            entry.grid(row=row_num, column=2)
            self.entries.append(entry)
            row_num += 1
        Button(self.master, text='OK', command=self.entry_handler, width=10).grid(row=9, column=1, sticky=S)
        Button(self.master, text='Cancel', command=self.master.destroy, width=10).grid(row=9, column=2, sticky=S)

    def entry_handler(self):
        record = [null_entry_handler(entry) for entry in self.entries if entry]
        add_record(self.report_type, record)
        self.master.destroy()


class Report(object):
    '''
    This is the most important class in this program. This class is for a window that is populated by data from a-
    customized report.
    '''
    def __init__(self, report_type, fields, total_amount=None, filter_by=None):
        self.report_type = report_type
        self.total_amount = total_amount
        self.filter_by = filter_by
        self.set_fields(fields)
        self.ordered_field = ()
        self.master = Toplevel()
        self.master.title('Reporting')
        self.master.iconbitmap('image/record.ico')
        self.prepare_images()
        self.canvas1 = Canvas(self.master)
        self.canvas2 = Canvas(self.master)
        self.refresh_report()

    def set_fields(self, fields):
        '''
        Sets the following three attributes: self.sp_field, self.display_fields, self.fields.
        '''
        self.sp_field = special_id[self.report_type]
        if self.sp_field not in fields:
            self.display_fields = list(fields)
            fields.insert(0,self.sp_field)
            self.fields = list(fields)
        else:
            self.fields = list(fields)
            self.display_fields = list(fields)

    def field_name_modifier(self, fields):
        '''
        Loops through fields concatenating their respective table names.
        Example: Phone --> contacts.Phone
        '''
        out = []
        for field in fields:
            new_name = field_name(field)
            out.append(new_name)
        return out

    def mixed_report_handler(self):
        if self.report_type == 'mixed':
            fields = list(self.field_name_modifier(self.fields))
        else:
            fields = list(self.fields)
        return fields

    def build_field_query(self):
        '''
        Returns the 'First_name, Last_name, Phone' string in the SQL statement:
        'SELECT First_name, Last_name, Phone FROM some_table'
        '''
        fields = self.mixed_report_handler()
        field_query = ''
        for field in fields:
            if fields_type_mapping[field] == self.report_type:
                field_query += field + ','
        return field_query

    def get_sql_data(self):
        '''
        Sets self.data with data pulled from SQL database
        '''
        field_query = self.build_field_query()
        sql_request = flexible_SQL(field_query[:-1], self.report_type, where=self.filter_by, order_by=self.ordered_field)
        self.data = pull_data(sql_request)

    def canvas_master_processs(self):
        '''
        Destroys old canvases, builds new ones, thereby refreshing.
        '''
        self.canvas1.destroy()
        self.canvas2.destroy()
        self.canvas1 = Canvas(self.master)
        self.canvas2 = Canvas(self.master)
        self.determine_button_width()
        self.layout_top()
        self.layout_headers()
        self.layout_buttons()
        self.canvas1.grid()
        self.canvas2.grid()

    def layout_top(self):
        '''
        Creates the report buttons for 'Custom', 'Refresh', and 'Excel'
        '''
        Button(self.canvas1,borderwidth=0,image=self.photo_custom,command=self.customize_report).grid(column=0, row=0)
        Button(self.canvas1,borderwidth=0,image=self.photo_refresh,command=self.refresh_report).grid(column=1, row=0)
        Button(self.canvas1,borderwidth=0,image=self.photo_excel,command=lambda: export(self.data)).grid(column=2, row=0)

    def layout_headers(self):
        '''
        Creates report headers
        '''
        iterator_column = 0
        for field in self.display_fields:
            text = field.replace('_',' ')
            text = text.replace('Address',' Address ')
            Button(self.canvas2,
                   text=text,
                   width=self.button_width[iterator_column],
                   height=1,
                   borderwidth=1,
                   font=('Corbel',10,'bold'),
                   anchor=W,
                   command=partial(self.custom_sort,iterator_column)).grid(row=1, column=iterator_column)
            iterator_column += 1

    def sized_record(self, record):
        if self.sp_field in self.display_fields:
            return record
        else:
            return record[1:]

    def layout_buttons(self):
        '''
        Lays out buttons
        '''
        iterator_row = 2
        total_index = self.get_total_index()
        for record in self.data:
            iterator_field = 0
            for field in self.sized_record(record):
                if record.index(field) == total_index:
                    Button(self.canvas2,text=field,width=self.button_width[iterator_field],height=1,borderwidth=0,command=partial(self.open_total_amount_window,record[0]),anchor=W).grid(row=iterator_row,column=iterator_field,sticky=S)
                else:
                    Button(self.canvas2,text=field,width=self.button_width[iterator_field],height=1,borderwidth=0,command=partial(self.open_record_window,record[0]),anchor=W).grid(row=iterator_row,column=iterator_field,sticky=S)
                iterator_field += 1
            iterator_row += 1

    def get_total_index(self):
        '''
        Returns the index for the field that is getting totalled, or None if n/a
        '''
        if 'Total_sales' in self.fields:
            return self.fields.index('Total_sales')
        return None

    def refresh_report(self):
        '''
        Submits a new SQL query and erases and lays out all GUI window elements.
        '''
        update_all_cust_totals()
        self.get_sql_data()
        self.canvas_master_processs()

    def customize_report(self):
        CustomizeReportWindow(self.report_type)

    def open_record_window(self, ID):
        RecordWindow(self.report_type, ID)

    def open_total_amount_window(self, ID):
        fields = list(type_to_fields['sales'])
        Report('sales',fields,filter_by=['Customer_ID', ID])

    def custom_sort(self, field_index):
        '''
        Reorders the report based on field and ascending or descending order. Receives input from field button. Sets-
        self.ordered_field attribute. Refreshes report.
        '''
        field = self.display_fields[field_index]
        flip = {'ASC' : 'DESC', 'DESC' : 'ASC'}
        if not self.ordered_field or self.ordered_field[0] != field:
            self.ordered_field = (field, 'ASC')
        elif self.ordered_field[0] == field:
            direction = flip[self.ordered_field[1]]
            self.ordered_field = (field, direction)
        else:
            raise Exception()
        self.refresh_report()

    def determine_button_width(self):
        '''
        This method loops through the fields, determining the max len for each field and setting self.button_width as-
        a list of those values. The purpose is aesthetic in that it makes it so column are sized roughly accordingly to-
        the length thats required, rather than uniformly across all fields.
        '''
        self.button_width = []
        for field in self.display_fields:
            ind = self.fields.index(field)
            max_value = self.list_of_list_column_len(self.data, ind, field)
            self.button_width.append(max_value)

    def list_of_list_column_len(self, list_of_lists, column, header):
        '''
        Return the max len for a single field
        '''
        max_value = len(header)
        for lst in list_of_lists:
            if len(str(lst[column])) > max_value:
                max_value = len(str(lst[column]))
        return max_value

    def prepare_images(self):
        self.photo_custom = ImageTk.PhotoImage(Image.open('image/custom.png'))
        self.photo_refresh = ImageTk.PhotoImage(Image.open('image/refresh_report.png'))
        self.photo_excel = ImageTk.PhotoImage(Image.open('image/excel.png'))


class CustomerCenter(Report):
    '''
    This window shows the customer name and how much in sales order came from them. It was an important lesson in-
    cross-referencing data from different tables.
    '''
    def __init__(self, report_type, fields, total_amount=None, filter_by=None):
        self.report_type = report_type
        self.total_amount = total_amount
        self.filter_by = filter_by
        self.sp_field = special_id[self.report_type]
        self.set_fields(fields)
        self.master = Toplevel()
        self.master.title('Reporting')
        self.master.iconbitmap('image/record.ico')
        self.prepare_images()
        self.canvas1 = Canvas(self.master)
        self.canvas2 = Canvas(self.master)
        self.refresh_report()

    def canvas_master_processs(self):
        '''
        Handles GUI.
        '''
        self.canvas1.destroy()
        self.canvas2.destroy()
        self.canvas3.destroy()
        self.canvas1 = Canvas(self.master)
        self.canvas2 = Canvas(self.master)
        self.canvas3 = Canvas(self.master, bg='blue')
        self.determine_button_width()
        self.layout_headers()
        self.layout_buttons()
        self.canvas1.grid(row=0)
        self.canvas2.grid(column=0, row=1)


class RecordWindow(object):
    '''
    This window displays a single contact record. It presents the user with the option to 'Edit', 'Exit', or 'Delete'.
    '''
    def __init__(self, report_type, ID):
        self.report_type = report_type
        self.sp_field = special_id[self.report_type]
        self.ID = ID
        self.fields = list(type_to_fields[report_type])
        self.width = 200
        self.height = 200
        self.entries = []
        self.master = Toplevel()
        self.master.iconbitmap('image/record.ico')
        self.set_data()
        self.build_canvas()

    def set_data(self):
        '''
        Sets the self.data attribute
        '''
        where = [self.sp_field, self.ID]
        sql_request = flexible_SQL('*', self.report_type, where=where)
        self.data = pull_data(sql_request)[0]


    def build_canvas(self):
        '''
        Handles primary gui elements
        '''
        self.canvas = Canvas(self.master, width=self.width, height=self.height)
        self.photo_edit = ImageTk.PhotoImage(Image.open('image/edit.png'))
        self.photo_exit = ImageTk.PhotoImage(Image.open('image/exit.png'))
        self.photo_delete = ImageTk.PhotoImage(Image.open('image/delete.png'))
        fields = list(self.fields)
        iterator = 0
        for field in fields:
            Label(self.canvas, text=field).grid(row=iterator, column=0, sticky=W)
            Label(self.canvas, text=self.data[iterator]).grid(row=iterator, column=1, sticky=W)
            iterator += 1
        Button(self.canvas, image=self.photo_edit, command=self.edit_record, borderwidth=0).grid(row=iterator, column=0)
        Button(self.canvas, image=self.photo_exit, command=self.master.destroy, borderwidth=0).grid(row=iterator, column=1)
        Button(self.canvas, image=self.photo_delete, command=self.delete_record, borderwidth=0).grid(row=iterator, column=2)
        self.canvas.grid()

    def edit_record(self):
        '''
        Binded handler for editing a record.
        '''
        self.canvas.destroy()
        self.canvas = Canvas(self.master, width=self.width, height=self.height)
        iterator = 0
        display_fields = list(self.fields)
        display_fields.remove(self.sp_field)
        for field in display_fields:
            Label(self.canvas, text=field).grid(row=iterator, column=0, sticky=W)
            iterator += 1
        iterator = 0
        Label(self.canvas, text=self.data[0]).grid(row=iterator, column=1, sticky=W)
        for field in self.data[1:]:
            a = StringVar()
            a.set(field)
            entry = Entry(self.canvas, width=15,textvariable=a)
            entry.grid(row=iterator, column=1)
            self.entries.append(entry)
            iterator += 1
        Button(self.canvas, text='Save', width=10, command=self.save_record).grid(row=iterator, column=0)
        Button(self.canvas, text='Cancel', width=10, command=self.master.destroy).grid(row=iterator, column=1)
        self.canvas.grid()

    def save_record(self):
        '''
        Handler for saving record
        '''
        record = [null_entry_handler(entry) for entry in self.entries if entry]
        record.append(self.ID)
        update_record(self.report_type, record)
        self.master.destroy()
        self.__init__(self.report_type, self.ID)

    def delete_record(self):
        '''
        Handler for deleting record
        '''
        delete_parameters = (self.report_type, self.sp_field, self.ID)
        DeleteRecordWindow(delete_parameters)
        self.master.destroy()


class CustomizeReportWindow(object):
    '''
    This window allows the user to customize the report fields.
    '''
    def __init__(self, report_type):
        self.report_type = report_type
        self.master = Toplevel()
        self.check_dict = {}
        self.fields = list(type_to_fields[self.report_type])
        self.layout()

    def layout(self):
        '''
        Manages GUI
        '''
        self.width = 100
        self.height = 100
        iterator = 1
        self.results = []
        for field in self.fields:
            self.check_dict[field]  = IntVar()
            Checkbutton(self.master, text=field, variable=self.check_dict[field],onvalue = 1, offvalue = 0).grid(row=iterator, sticky=W)
            iterator += 1
        Button(self.master, text='Run Report', command=self.call_report, width=15).grid(row=iterator)

    def clean_dict(self):
        for key in self.check_dict.keys():
            self.check_dict[key] = self.check_dict[key].get()

    def call_report(self):
        self.clean_dict()
        fields = [field.replace(' ','_') for field in self.check_dict.keys() if self.check_dict[field] == 1]
        self.master.destroy()
        Report(self.report_type,fields)




class DeleteRecordWindow(object):
    '''
    This window the user encounters when they are deleting a contact record.
    '''
    def __init__(self, parameters):
        self.parameters = parameters
        self.master = Toplevel()
        self.master.title('Delete Record')
        Label(self.master, text='Are you sure you want to DELETE this record?').grid()
        Button(self.master,text='Ok', width=15, command=self.ok).grid()
        Button(self.master,text='Cancel', width=15, command=self.master.destroy).grid()

    def ok(self):
        table, field, criteria = self.parameters
        self.master.destroy()
        delete_where(table, field, criteria)




def run():
    HomeScreen()

