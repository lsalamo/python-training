import requests
import pandas as pd
import os
import sys

# =============================================================================
# VARIABLES
# =============================================================================

def init():
    # Change working directory
    os.chdir('/Users/luis.salamo/Documents/github enterprise/python-training/adobe/health-metrics-comparison')
    
    # Set list report suites
    data_values = variables['rs'].values()
    variables['list_rs'] = list(data_values)
    print('> init() -', 'loaded')


# =============================================================================
# REQUEST ADOBE ANALYTICS
# =============================================================================

def get_adobe_analytics_data():
    print('')
    file = open('aa/request.json')
    payload = file.read()
    file.close()
    print('> get_adobe_analytics_data() -', 'file payload loaded')

    url = 'https://analytics.adobe.io/api/schibs1/reports'
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + variables['token'],
      'x-api-key': '5e9fd55fa92c4a0a82b3f2a74c088e60',
      'x-proxy-global-company-id': 'schibs1'
    } 
    df = pd.DataFrame();
    for row in variables['list_rs']:
        print('> get_adobe_analytics_data() - rs:', row)
        response = requests.request('POST', url, headers=headers, data=payload.replace('{{rs}}', row))
        if response.status_code != 200:
            sys.exit('ERROR ' + str(response.status_code) + ' > ' + response.text)
        else:
            response = response.json()
            total_records = response['numberOfElements']
            if total_records > 0:
                df_request = pd.DataFrame.from_dict(response['rows'])
                df_request['rs'] = row
                df_request['day'] = pd.to_datetime(df_request['value']).dt.strftime('%Y%m%d')
                df_request[['web-visits', 'web-visitors', 'and-visits', 'and-visitors', 'ios-visits', 'ios-visitors']] = pd.DataFrame(df_request['data'].tolist(), index= df_request.index).astype('int64')
                df = pd.concat([df, df_request])
        print('> get_adobe_analytics_data() -', 'data loaded')
        
    
    # Clean dataframe
    df.drop(['itemId', 'data', 'value'], axis=1, inplace=True)
    df['day'] = df['day'].astype('str')
    print('> get_adobe_analytics_data() -', 'clean dataframe loaded')
    
    return df

def get_adobe_analytics_data_events():
    print('')
    file = open('aa/request-events.json')
    payload = file.read()
    file.close()
    print('> get_adobe_analytics_data_events() -', 'file payload loaded')

    url = 'https://analytics.adobe.io/api/schibs1/reports'
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + variables['token'],
      'x-api-key': '5e9fd55fa92c4a0a82b3f2a74c088e60',
      'x-proxy-global-company-id': 'schibs1'
    } 
    df = pd.DataFrame();
    for row in variables['list_rs']:
        print('> get_adobe_analytics_data_events() - rs:', row)
        response = requests.request('POST', url, headers=headers, data=payload.replace('{{rs}}', row))
        if response.status_code != 200:
            sys.exit('ERROR ' + str(response.status_code) + ' > ' + response.text)
        else:
            response = response.json()
            total_records = response['numberOfElements']
            if total_records > 0:
                df_request = pd.DataFrame.from_dict(response['rows'])
                df_request['rs'] = row
                df_request['event'] = df_request['value']
                df_request[['web', 'and', 'ios']] = pd.DataFrame(df_request['data'].tolist(), index= df_request.index).astype('int64')
                df = pd.concat([df, df_request])
        print('> get_adobe_analytics_data_events() -', 'data loaded')
        
    
    # Clean dataframe
    df.drop(['itemId', 'data', 'value'], axis=1, inplace=True)
    df['event2'] = df['event'].str.lower().replace(' ', '_', regex=True)
    print('> get_adobe_analytics_data_events() -', 'clean dataframe loaded')
    
    return df

# =============================================================================
#   REQUEST GOOGLE ANALYTICS
# =============================================================================

def get_google_analytics_data():
    print('')
    df = pd.DataFrame();
    dir = os.path.join(variables['directory'], 'ga')
    if os.path.isdir(dir):
        df = pd.read_csv(dir + '/data_health_metrics_comparison.csv', index_col=False)
    print('> get_google_analytics_data() -', 'data loaded')
    
    # Clean dataframe
    df.drop(df.index[:1], inplace=True)
    df.drop(['Totals', 'Totals.1'], axis=1, inplace=True)
    df.columns = ['day', 'and-visits', 'and-visitors', 'web-visits', 'web-visitors', 'ios-visits', 'ios-visitors']
    df['day'] = df['day'].astype('int64').astype('str')

    print('> get_google_analytics_data() -', 'clean dataframe loaded')
    return df

def get_google_analytics_data_events():
    print('')
    df = pd.DataFrame();
    dir = os.path.join(variables['directory'], 'ga')
    if os.path.isdir(dir):
        df = pd.read_csv(dir + '/data_health_metrics_comparison_events.csv', index_col=False)
    print('> get_google_analytics_data_events() -', 'data loaded')
    
    # Clean dataframe
    df.drop(df.index[:1], inplace=True)
    df.drop(['Totals'], axis=1, inplace=True)
    df.columns = ['event2', 'web', 'and', 'ios']
    df['web'] = df['web'].astype('int64')
    df['and'] = df['and'].astype('int64')
    df['ios'] = df['ios'].astype('int64')

    print('> get_google_analytics_data_events() -', 'clean dataframe loaded')
    return df

# =============================================================================
#   JOIN
# =============================================================================

def get_data(rs):
    print('')
    df_aa = result['df_aa'].loc[result['df_aa'].rs == rs]
    df = df_aa.join(result['df_ga'].set_index('day'), on='day',lsuffix='-aa', rsuffix='-ga')
    result['df_web'] = df[['day', 'web-visits-aa', 'web-visitors-aa', 'web-visits-ga', 'web-visitors-ga']]
    result['df_android'] = df[['day', 'and-visits-aa', 'and-visitors-aa', 'and-visits-ga', 'and-visitors-ga']]
    result['df_ios'] = df[['day', 'ios-visits-aa', 'ios-visitors-aa', 'ios-visits-ga', 'ios-visitors-ga']]    

    print('> get_data() -', 'data loaded')
    return df

def get_data_events(rs):
    print('')
    df_aa = result_events['df_aa_events'].loc[result_events['df_aa_events'].rs == rs]
    df = pd.merge(df_aa, result_events['df_ga_events'], on='event2',suffixes=('-aa', '-ga'), how='outer')
    result_events['df_web_events'] = df[['event2', 'web-aa', 'web-ga']]
    result_events['df_android_events'] = df[['event2', 'and-aa', 'and-ga']]
    result_events['df_ios_events'] = df[['event2', 'ios-aa', 'ios-ga']]    

    print('> get_data_events() -', 'data loaded')
    return df
 
# =============================================================================
#   MAIN
# =============================================================================

result = {}
result_events = {}
variables = {}
variables['rs'] = {}
variables['token'] = 'eyJhbGciOiJSUzI1NiIsIng1dSI6Imltc19uYTEta2V5LTEuY2VyIiwia2lkIjoiaW1zX25hMS1rZXktMSIsIml0dCI6ImF0In0.eyJpZCI6IjE2NDU1MjIwNTY0MzJfMmM0ZmFiMzQtYjkzOC00MjE3LWE3NDctMDE3YTQ3YjgxODJjX3VlMSIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJjbGllbnRfaWQiOiI1ZTlmZDU1ZmE5MmM0YTBhODJiM2YyYTc0YzA4OGU2MCIsInVzZXJfaWQiOiJBRDRBN0ExRDYwODhGOUY0MEE0OTVDNjhAdGVjaGFjY3QuYWRvYmUuY29tIiwiYXMiOiJpbXMtbmExIiwiYWFfaWQiOiJBRDRBN0ExRDYwODhGOUY0MEE0OTVDNjhAdGVjaGFjY3QuYWRvYmUuY29tIiwiY3RwIjowLCJmZyI6IldHNFRPQ0o2RkxFNUlQVUNFTVFGUkhRQVNBPT09PT09IiwibW9pIjoiYTFjZGMwNWIiLCJleHBpcmVzX2luIjoiODY0MDAwMDAiLCJjcmVhdGVkX2F0IjoiMTY0NTUyMjA1NjQzMiIsInNjb3BlIjoib3BlbmlkLEFkb2JlSUQscmVhZF9vcmdhbml6YXRpb25zLGFkZGl0aW9uYWxfaW5mby5wcm9qZWN0ZWRQcm9kdWN0Q29udGV4dCJ9.RM3YhzRpCkiEpygdQf13c92U7gU4HTmadHQKYi9NOtpw1AHia3VtcGncpCX4in_6hVDwqH-6DfUviLPEb7YMYBgNokxkdLJb5JRWjwPs41JuPPGrRqmT8GvW5etBFKkclk340LaO8s3DZx8VO6g3WLUI1vlY2D8mB49raAeZnbA9D6y4xEYmK3LSska5CpZ5YaoPvEvnHWmrGcunLcQRZ8yMB4SZwgIWTqsUS3Nxcy3n-c5-i6vRwfwoL_4AAL9pLgGiijCf9CIu-tz_nlUoXDeFPRRUKVz8G7D3J_06ZKOgPGhK0DWR77kX6Vz75RBUbiD1cHGpnjfsgF1f5rRoig'
variables['directory'] = '/Users/luis.salamo/Documents/github enterprise/python-training/adobe/health-metrics-comparison'
variables['rs']['rs_fotocasaes'] = 'vrs_schibs1_fcall'
variables['rs']['rs_motosnet'] = 'vrs_schibs1_motorcochesnet'
variables['from_date'] = '2021-02-01'
variables['to_date'] = '2021-02-01'

init()

result['df_aa'] = get_adobe_analytics_data()
result['df_ga'] = get_google_analytics_data()
result['df'] = get_data(variables['rs']['rs_fotocasaes'])

result_events['df_aa_events'] = get_adobe_analytics_data_events()
result_events['df_ga_events'] = get_google_analytics_data_events()
result_events['df'] = get_data_events(variables['rs']['rs_fotocasaes'])


# # =============================================================================
# #   REQUEST GOOGLE ANALYTICS
# # =============================================================================

# def set_adobe_analytics_export_csv():
#     dir = os.path.join(variables['directory'], 'aa')
#     if os.path.isdir(dir):
#         shutil.rmtree(dir)
#     os.makedirs(dir)
#     result['df_aa'].to_csv(dir + '/data_health_metrics_comparison.csv')
#     print('> set_adobe_analytics_export_csv() -', 'export loaded')
    



