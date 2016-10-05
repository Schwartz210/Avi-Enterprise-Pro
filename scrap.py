def option1(self, field_query):
    if self.filter_by:
        return select_fields_where(field_query[:-1],report_type, filter_by[0],filter_by[1])
    else:
        return select(field_query[:-1], report_type)


def option2(self, field_query):
    if self.filter_by:
        sql_request = select_fields_where(field_query[:-1],report_type, filter_by[0],filter_by[1])
    else:
        sql_request = select(field_query[:-1], report_type)
    return sql_request