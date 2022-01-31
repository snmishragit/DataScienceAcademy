from distutils.log import error
from turtle import width
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
        df_cs.insert(0,'Candidate_ID', range(1, 1 + len(df_cs)))
        path = 'C://Temp/capstone_data.csv'
        df_cs.to_csv('C://Temp/capstone_data.csv', encoding='utf-8')
        
        return path
        
    except:
        print('Error')
def convert_df_to_csv(df):
    return df.to_csv().encode('utf_8')

def draw_plot_scatter(df_capstone):    
    #get parameter lists like states and gender and age
    lst_states =  list(df_capstone.state.unique())
    lst_gender = list(df_capstone.gender.unique())
    lst_age = list(df_capstone.age.unique())
    lst_home_comp = list(df_capstone.home_computer.unique())
    #set up Streamlit page
    #gender = st.sidebar.selectbox("Please select a gender: ", ['Male', 'Female'])
    st.set_page_config(layout='wide')
    st.sidebar.write('# Filter Data')
    #gender = st.sidebar.selectbox("Please select a gender: ", lst_gender)
    
    is_home_comp = st.sidebar.radio("Used home computer?", lst_home_comp)
    st.title('Capstone Project: DSA 2022')
    st.write('## Data Input for the Capstone Project')
    #Download Button 
    csv_file = convert_df_to_csv(df_capstone.filter(items=['rt_total','sum_score','gender','state','home_computer','age']))
    st.download_button(
        label="Download data as CSV",
        data=csv_file,
        file_name='df_capstone.csv',
        mime='txt/csv'
    )
    st.dataframe(df_capstone.filter(items=['rt_total','sum_score','gender','state','home_computer','age']), 800, 300)
    #st.plotly_chart(fig1)
    sel_values = st.sidebar.slider('Select age range to view the results', 18, 80, (18,80) )
    minval = sel_values[0]
    maxval = sel_values[1]
    st.write("## Performance Analysis")
    st.write('### Selected age range:', sel_values)
    st.write('### Used home computer:', is_home_comp )
    st.write("### Figure 1")    
      
    fig1 = px.histogram(df_capstone.query('home_computer==@is_home_comp and (age >= @minval and age <= @maxval)'), x="state", y="sum_score",  color="gender", hover_name="rt_total") 
    #fig1 = px.histogram(df_capstone.query('home_computer==@is_home_comp and (age >= @minval and age <= @maxval)'), x="state", y="sum_score",  color="rt_total", hover_name="gender", facet_row='gender' ) 
    st.plotly_chart(fig1, use_container_width=True, sharing="streamlit")

    st.write("### Figure 2")  
    
    fig2 = px.bar(df_capstone.query('home_computer==@is_home_comp and (age >= @minval and age <= @maxval)'), x="state", y="sum_score",color='gender', hover_name="rt_total", facet_col='gender')
    #fig2 = px.sunburst(df_capstone.query('home_computer==@is_home_comp and (age >= @minval and age <= @maxval)'), path=['state', 'gender', 'sum_score'], values='rt_total', color='age')   
    st.plotly_chart(fig2, use_container_width=False, sharing="streamlit")
    return
def main():
    path_cs = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/data_capstone_dsa2021_2022.csv'
    path_st = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/states.csv'
    path_clean = 'C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/DataScienceAcademyHomework/DataScienceAcademy/CapstoneSM/Data/data_capstone4.csv'
    delimiter = ','
    df_capstone_path = 'C://Temp/capstone_data.csv'
    #One time clean
    #read_write_csv_file(path_cs,path_clean) One time clean
    # cleaned dataframe 
    if(df_capstone_path == ""):
        df_capstone_path = get_clean_parsed_data(path_clean, path_st, delimiter)
    else:
        pass
    # generate plot graphs
    try:

        df_capstone = read_file_to_data_frame(df_capstone_path,delimiter)    
        draw_plot_scatter(df_capstone)
    except BaseException as err:
        print(err)
        raise
    return

main()
    