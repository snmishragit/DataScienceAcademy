import fuzzywuzzy
from fuzzywuzzy import fuzz
import pandas as pd
import csv
import streamlit as st
import plotly.express as px

#######################################################
# Matches the States in Data file to real state
# ####################################################### 
def match_states(statename, list_names, list_abbrs, min_score=0):
    max_score = -1
    max_name = ''
    for x in list_names:
        #print(x)
        #score = fuzz.partial_ratio(statename.lower(), x.lower()) 
        score = fuzz.token_sort_ratio(statename.lower(), x.lower()) 
        if (score > min_score) & (score > max_score):
            max_name = x   
            #print(max_name)
            max_score = score
            
        if(max_score < 75):
            # look in the abbr list
            for a in list_abbrs:
                score = fuzz.ratio(statename.lower(), a.lower()) 
                if (score > min_score) & (score > max_score):
                    if(statename.lower() == ''):
                        max_name = 'Other'
                        max_score = '0'
                    else:
                        max_name = a
                        max_score = score
    
    
    return (max_name, max_score)
#######################################################
# Reads the file into pandas Dataframe
# #######################################################  
def read_file_to_data_frame(filePath, delimiter):    
    df = pd.read_csv(filePath,sep=delimiter)
   # print(df.head)
    return df
#######################################################
# Reads the provided csv data file and cleans data and writes to a new file
# #######################################################  

def read_write_csv_file(readfilePath, writefilepath):
    # header row
    header = []
    rows = []
    with open(readfilePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                header.append(row)
                line_count += 1
            else:                                
                strloc = row[-2]
                #print(f'\t{strloc}')                
                nrow = row
                line_count += 1
                if(strloc.find(",") >= 0):
                    #print(strloc)
                    strr = strloc.replace(',', ' ')
                    nrow[-2] = strr
                    #print(f'\t{nrow[-2]}')
                    rows.append(nrow)
                else:
                    rows.append(row)
                    #print(nrow)
    
    print(f'Processed {line_count} lines.')
    
    with open(writefilepath, mode='w') as csvw_file:        
        #writer = csv.DictWriter(csv_file, fieldnames=header)
        writer = csv.writer(csvw_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        print("rows count" + str(len(rows)))
        for wrow in rows:
            writer.writerow(wrow)
                
def get_state_dictionary(df_sts):
    lst_st = []
    dict_st = df_sts.to_dict(orient='records')
    dict_ct = {}
    for row in dict_st:
       # print(row)
        #print(row['name'])
        dict_ct[row['name']] = row['abbr']
        
    for a in dict_st:
       # print(a)
        dict_ct[a['abbr']] = a['abbr']
    
    # Add valid 'Other'
    
    dict_ct['Other'] = 'Other'
    
    return dict_ct

def get_clean_parsed_data(path_cs, path_st, delimiter):
    
    try:     

        df_cs = read_file_to_data_frame(path_cs, delimiter)    
        df_st = read_file_to_data_frame(path_st, '\t')
       # print(df_st.head)
        dict_sts = get_state_dictionary(df_st)
       # print(dict_sts)
        #print(dict_sts['NJ'])
        lst_cs_states = list(df_cs.state)
        
        #list of State Names
        lst_st_names = list(df_st.name.unique())
        #print(lst_st_names)
        #list of state abbr
        lst_st_abbr = list(df_st.abbr.unique())
        #print(lst_st_abbr)

        #get final list assign to the bucket Other if the states are not recognizable
           # missingKeyList = []
        for s in lst_cs_states:
            #print(s)
            if s in dict_sts:
                pass            
            else:
                #print(s)
               # dict_sts[s] = 'Other'
                pass
        
       # print(dict_sts)
        # Add keys and values in a dictionary
        lst_sts = []
                
        for x in lst_cs_states:
            #print(x)
            match = match_states(x, lst_st_names, lst_st_abbr, 0)
            #print(match)
            if match[1] > 0:
                #print(str(dict_sts[match[0]]))
                name1 = (str(dict_sts[match[0]]))                
                name = ( str(x), name1)
                lst_sts.append(name)
        state_dict = dict(lst_sts)              
        df_cs.state  = df_cs.state.replace(state_dict)
        #print(df_cs)
        return df_cs
        
    except:
        print('Error')

def draw_plot_scatter(df):
    fig1 = px.scatter(df, x="sum_score", y="rt_total", size="Candidate_ID", color="gender")
    fig2 = px.histogram(df, x="sum_score", color="state", facet_col='gender')
    
    fig1.show()
    fig2.show()
    return
def main():
    path_cs = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/data_capstone_dsa2021_2022.csv'
    path_st = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/states.csv'
    path_clean = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/data_capstone4.csv'
    delimiter = ','
    #One time clean
    #read_write_csv_file(path_cs,path_clean) One time clean
    # cleaned dataframe 
    df_capstone = get_clean_parsed_data(path_clean, path_st, delimiter)
    # generate plot graphs
    draw_plot_scatter(df_capstone)
    return

main()
    