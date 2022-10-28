from datetime import timedelta
import datetime as dt 
import airflow
from airflow.models import DAG 
from airflow.operators.python_operator import PythonOperator , BranchPythonOperator
from airflow.operators.bash_operator import BashOperator 
from airflow.operators.dummy_operator import DummyOperator 
from airflow.operators.http_operator import SimpleHttpOperator 
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
 
# from airflow_dags_devops_apps_pol.devops_teams_utilities import trigger_teams
from sqlite3 import connect
import json
from webbrowser import get
from airflow_dags_devops_apps_pol.config import devops_airflow_common_conf
from airflow_dags_devops_apps_pol.devops_monitoring_utilities import msteams_on_task_failure_callback
# from airflow.exceptions import AirflowSkipException 
# import subprocess
import os 
# import shutil
# import sys
# import logging
from io import StringIO

import datetime as dt
import time

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from airflow.hooks.base_hook import BaseHook

from dateutil.parser import *   
# import calendar



def get_grafana_dashboards_backups(**ti):
    TOKEN = "******"
    auth=HTTPBasicAuth(
            BaseHook.get_connection("devops_apps_pol_grafana").login,
            BaseHook.get_connection("devops_apps_pol_grafana").password,
        )
    TOKEN = auth.password
    connection = {
        "proxies" : {'http': 'socks5h://192.168.67.2:1081', 'https': 'socks5h://192.168.67.2:1081'},
        "token" : auth.password,
        "headers" : {'Accept': 'application/json',"Authorization": "Bearer "+ TOKEN},
        "link"    : "https://grafana-centralized-monitoring.advantagedp.org/api/search",
        "linkfolders"   : "https://grafana-centralized-monitoring.advantagedp.org/api/folders",
        "link_db" : "https://grafana-centralized-monitoring.advantagedp.org/api/folders/ZsM-EZyZk", # folder
        "linkf"   : "https://grafana-centralized-monitoring.advantagedp.org/api/folders/id/778",
        "link_search" : "https://grafana-centralized-monitoring.advantagedp.org/api/search?query=&",
        "link_json"   : "https://grafana-centralized-monitoring.advantagedp.org/api/dashboards/uid/"
  

    }

#     mkdir -p dashboards && for dash in $(curl -k -H "Authorization: Bearer $KEY" $HOST/api/search\?query\=\& |tr ']' '\n' |cut -d "," -f 5 |grep slug |cut -d\" -f 4); do 
#   curl -k -H "Authorization: Bearer $KEY" $HOST/api/dashboards/db/$dash > dashboards/$dash.json 
# done
    res = requests.get(connection['link'], headers=connection['headers'],  verify=False)
    folders = requests.get(connection['linkfolders'], headers=connection['headers'], verify=False)
    # print( 'res ',res )
    # print( 'folders ',folders )

    res = res.json()
    folders = folders.json()
    # print( folders )
    idF,uidF, titleF, = zip(
        *(
            (
                item["id"],
                item["uid"],
                item["title"],                
            )
            for item in folders
        )
    )
    df_folders = pd.DataFrame(
        {
            "Id": idF,
            "Uid": uidF,
            "Title": titleF,

        }
    )
    
    # print(f' \n {df_folders[0:10]} \n ')
    id,uid, title, uri,url, slug, type_ ,tags, isStarred,  sortMeta = zip(#folderId,folderUid, folderTitle, folderUrl
        *(
            (
                item["id"],
                item["uid"],
                item["title"],
                item["uri"],
                item["url"],
                item["slug"],
                item["type"],
                item["tags"],
                item["isStarred"],       
                item["sortMeta"],
                
            )
            for item in res
        )
    )
    df = pd.DataFrame(
        {
            "Id": id,
            "Uid": uid,
            "Title": title,
            "Uri": uri,
            "Url": url,
            "Slug": slug,
            "Type": type_,
            "Tags": tags,
            "IsStarred": isStarred,
            "SortMeta": sortMeta,
        }
    )
    # print(  df[0:15:2] ) 
    # print( df.iloc[12])
    boson = df.iloc[12]
    df['Boson'] = df['Tags'].apply( lambda x : True if 'boson' in ''.join(x).lower() else False )
    boson = df[df['Boson']==True]
    def make_link(text , link = connection['link_json']):
        return link + text
    dir_path = 'Boson'
    today = dt.datetime.now()
    print(' date of taday year {} montg {} day {}'.format( today.year, today.month, str(today.day)))
    
    dir_path = f'{dir_path}_{str(today.year)}_{str(today.month)}_{str(today.day)}'
    def make_files(name, link ):
        tresc = requests.get(link, headers=connection['headers'], verify=False)
        tresc.text.replace(" ","") # CHYBA BEZ SENSU ------------------------------
        tresc = tresc.json()
        lista = list(tresc.keys())
        print( f'{len(tresc)}, {type(tresc)} \n {list(tresc.keys())} \n {tresc}') 
        for key, item in tresc.items():
            print( f'key - {key}   \n{tresc[key]}')
            # for k , v in tresc[key].items():
            #     print( f' k - {tresc[key][k]}')
        name = name + '.json'
        folder = r'/mapr/dp.stg.munich/ad-vantage/deploy/airflow/devops/airflow-stg/dags/airflow_dags_devops_apps_pol'
        # plik = open( os.path.join(folder,name))
        # plik.write(tresc)
        # plik.close()
        # with open(name , 'w' , encoding='utf-8') as file:
        #     json.dump( tresc , file)
        # shutil.copy(name,dir_path)
    boson['Name'] = boson['Title'].apply( lambda x : x.replace(" ","_")) 
    boson['Links'] = boson['Uid'].apply( make_link)
    dir_path = 'Boson'
    today = dt.datetime.now()
    
    dir_path = f'{dir_path}_{str(today.year)}_{str(today.month)}_{str(today.day)}'
    print( f'dir_path {dir_path}')
    print( f'where am i {os.getcwd()}')
    list_directories = os.listdir()
    print( list_directories)
    # /mapr/dp.stg.munich/ad-vantage/deploy/airflow/devops/airflow-stg/dags/airflow_dags_devops_apps_pol
    
    # if dir_path  in list_directories:
    #     print( f' DIRECTORIE {dir_path} EXISTS ')
    # else:
    #     os.mkdir(dir_path)
    # print( boson.head() )
    for ind in boson.index:
        # print( boson['Name'][ind] , boson['Links'][ind] )
        make_files(boson['Name'][ind], boson['Links'][ind]  )
    print( f'THIS IS df \n {df.iloc[9:13]} \n')
    print( f'THIS IS df_folders \n {df_folders.iloc[9:13]} \n')
    print( f'THIS IS boson \n {boson.iloc[:]} \n')
    print( ' PROBA ZAPISANIA PLIKU NA CLASTRZE \n')
    # os.mkdir(r'/mapr/dp.stg.munich/ad-vantage/deploy/airflow/devops/airflow-stg/dags/airflow_dags_devops_apps_pol/test.txt')
    # lista = os.listdir(r'/mapr/dp.stg.munich/ad-vantage/deploy/airflow/devops/airflow-stg/dags/airflow_dags_devops_apps_pol')

    # # return df , df_folders , boson

# all_backups, foldery , boson = get_grafana_dashboards_backups()[0]  ,   get_grafana_dashboards_backups()[1] ,get_grafana_dashboards_backups()[2]


ARGS ={
    "queue": "tu-devops-apps-pol",
    "owner":"devops_apps_pol-s",
    "retries": 3,
    "email_on_failure": False,
    "on_failure_callback": msteams_on_task_failure_callback,
    'start_date':airflow.utils.dates.days_ago(1),
}

with DAG(
    dag_id='devops_monitoring_grafana_dashboards_backup',
    default_args=ARGS,
    schedule_interval='01 20 * * *',
    default_view="graph",
    tags=["teams", "boson","grafana"],
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
) as dag:



    t_dummy = DummyOperator(
        task_id='dummy',
        dag=dag,    
        )

    t_bash_hello = BashOperator(
    task_id='bash_hello',
    bash_command='echo Hello i am BashOperator ',
    dag=dag,
    )
    # t_whoami = BashOperator(
    # task_id='whoami',
    # bash_command="whoami",
    # dag=dag,
    # )
    # t_where = BashOperator(
    # task_id='where',
    # bash_command="ls -l",
    # dag=dag,
    # )

    # USE ON PROD - RUN BASH SCRIPT
    ssh_grafana_dashboards_backups = SSHOperator(
        ssh_conn_id="devops_apps_pol_ssh",
        task_id="ssh_grafana_dashboards",
        # command="bash /mapr/dp.stg.munich/user/devops_apps_pol-s/grafana/dashboards/grafana_dashboards.sh",
        # command="ls /mapr/dp.stg.munich/user/devops_apps_pol-s/grafana/dashboards/",# && bash /mapr/dp.stg.munich/user/devops_apps_pol-s/grafana/dashboards/grafana_dashboards.sh",
        command="bash /mapr/dp.stg.munich/user/devops_apps_pol-s/grafana/dashboards/grafana_dashboards.sh ", # STG 
        # command="bash /mapr/dp.prod.munich/user/devops_apps_pol-s/grafana/dashboards/grafana_dashboards.sh ", # PROD
        trigger_rule="all_done",
        do_xcom_push=True,
    )

    t_grafana_dashboards = PythonOperator(
        task_id='t_grafana_dashboards',
        python_callable=get_grafana_dashboards_backups,
        provide_context=False,
        xcom_push=True,
        retries=3,
        dag=dag, 
    )

    t_dummy >> t_bash_hello >> t_grafana_dashboards

    t_dummy >> ssh_grafana_dashboards_backups

    

