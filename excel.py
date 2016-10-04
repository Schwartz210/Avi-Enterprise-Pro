__author__ = 'aschwartz - Schwartz210@gmail.com'
import csv


def export(data):
    file = open(r'H:\test.csv', 'w', newline='')
    write = csv.writer(file)
    write.writerows(data)
    file.close()


