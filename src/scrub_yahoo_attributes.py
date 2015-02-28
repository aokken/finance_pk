'''
Created on Jan 27, 2014

@author: aaron
'''
import csv

def main():
    options_file = open('/home/aaron/Documents/yahoo_finance_options.csv', 'rb')
    reader = csv.reader(options_file, delimiter=',', quotechar='"')
    
    print "{"
    for op in reader:
        print "'{0}' : {{'description' : '{1}', 'chars' : '{2}'}},".format(op[0], op[1], op[2])
    print "}"
    
    options_file.close()
    
if __name__ == '__main__':
    main()