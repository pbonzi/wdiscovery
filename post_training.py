import watson_developer_cloud
import json
import csv
import requests
import sys
import time
from pathlib import Path
import configparser

class myDiscovery:

    def initVariables(self):
        global env_id
        global coll_id
        global service_username
        global service_password
        global version
        global discovery

        #Use the SDK to create a new Disovery Client.
        discovery = watson_developer_cloud.DiscoveryV1(
            version,
            username=service_username,
            password=service_password)

    def cleanData(self):
        global env_id
        global coll_id
        global discovery
        print('Removing all training data...\n')
        #Remove all training data set before to start
        discovery.delete_all_training_data(env_id,coll_id)
        print('Cleaning complete.')

    def loadCSV(self,filestr="./training_data_test.csv"):
        global env_id
        global coll_id
        global discovery
        print('CSV file "',filestr,'" is loading...\n')
        start_time = time.time()
        count=0
        my_file = Path(filestr)
        if(my_file.is_file()):
            #open the training file and create new training data objects
            with open(my_file, encoding='utf-8') as training_doc:
                training_csv = csv.reader(training_doc, delimiter=',')
                training_obj = {}
                training_obj["examples"] = []
            
                #create a new object for each example 
                #There can be more than one example per Query, so we have to loop over all that exist in the row and create a list for each example
                for row in training_csv:
                    #Create a Traiinig obj dictionary, not really needed, but still included as I used to use it
                    training_obj = {}
                    #Create a dictionay key examples with a value of an empty list
                    training_obj["examples"] = []
                    #Create a dictionay key natural_language_query with a value of column a from this row of the training file
                    training_obj["natural_language_query"] = row[0]
                    #Counter for the columns
                    i = 1
                    #Gets the number of examples that are in the csv file. only works for csv files formatted the same as the sample I gave you.
                    #This 'looplen' variable must be amended accordingly to the CSV file structure
                    looplen= int((((len(row))-1)/3)+1)
                    for j in range(0,looplen):
                        #Checks that the cell is not empty
                        if row[i] != "":
                            #Create a example_obj dictionary
                            example_obj = {}
                            #Create a key "relevance" in the dictionary and add the contents of row[i] as the value
                            example_obj["relevance"] = row[i]
                            #Create a key "document_id" in the dictionary and add the contents of row[i+1] as the value
                            example_obj["document_id"] = row[i+1]
                            #Create a key "examples" in the training_obj dict, if it doesn't exist and add example_obj as a list item 
                            training_obj["examples"].append(example_obj)
                        #This 'i' variable must be amended accordingly to the CSV file structure
                        #each example takes 2 columns, so go to the next one
                        i = i + 2
                    #send the training data to the discovery service 
                    discovery.add_training_data(env_id, coll_id,natural_language_query=training_obj["natural_language_query"],filter=None, examples=training_obj["examples"])
                    count+=1
            elapsed_time = time.time() - start_time
            print('Training completed.',count, ' documents trained in (',round(elapsed_time,2),'secs)')  
            training_doc.close()
        else:
            # doesn't exist
            print('Wrong file name or path.')

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

Config = configparser.ConfigParser()
Config.read("./discovery.ini")

service_username = ConfigSectionMap("DiscoveryCredentials")['username']
service_password = ConfigSectionMap("DiscoveryCredentials")['password']
env_id = ConfigSectionMap("DiscoverySettings")['environment']
coll_id = ConfigSectionMap("DiscoverySettings")['collection']
version = ConfigSectionMap("DiscoverySettings")['version']

wd = myDiscovery()
wd.initVariables()

while(True):
    command = input('Available commands:\n1: cleaning data\n2: load CSV file\n3: Exit\nEnter your command:')
    if command=='1':
        wd.cleanData()
    elif command=='2':
        print('Sample file: ./training_data_test.csv')
        CSVfile = input('CSV path/filename: ')
        wd.loadCSV(CSVfile)
    elif command=='3':
        break
print('Application closing.')