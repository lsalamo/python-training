import requests
import pandas as pd
import functions as f
import dt as dt


class API:
    def __init__(self, method, url, headers, payload):
        self.method = method
        self.url = url
        self.headers = headers
        self.payload = payload

    def request(self):
        df = pd.DataFrame()
        response = requests.request(self.method, self.url, headers=self.headers, data=self.payload)
        if response.status_code != 200:
            f.Log.print_and_exit('API.request', str(response.status_code) + ' > ' + response.text)
        else:
            response = response.json()
            total_records = response['numberOfElements']
            if total_records > 0:
                df = pd.DataFrame.from_dict(response['rows'])
        return df


class Adobe_API(API):
    rs_fotocasaes = 'vrs_schibs1_fcall'
    rs_cochesnet = 'vrs_schibs1_motorcochesnet'
    rs_motosnet = 'vrs_schibs1_motormotosnet'

    def __init__(self, method, url, token, payload):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
            'x-api-key': '5e9fd55fa92c4a0a82b3f2a74c088e60',
            'x-proxy-global-company-id': 'schibs1'
        }
        super().__init__(method, url, headers, payload)


class Adobe_Report_API(Adobe_API):

    def __init__(self, rs, token, url_request, date_from, to_date):
        # endpoint
        url = 'https://analytics.adobe.io/api/schibs1/reports'

        # date
        date_from = dt.Datetime.str_to_datetime(date_from, '%Y-%m-%d')
        date_from = dt.Datetime.datetime_to_str(date_from, '%Y-%m-%dT00:00:00.000')
        to_date = dt.Datetime.str_to_datetime(to_date, '%Y-%m-%d')
        to_date = dt.Datetime.datetime_add_days(to_date, 1)
        to_date = dt.Datetime.datetime_to_str(to_date, '%Y-%m-%dT00:00:00.000')
        date = date_from + '/' + to_date

        # payload
        file = f.File(url_request)
        payload = file.read_file()
        payload = payload.replace('{{rs}}', rs)
        payload = payload.replace('{{dt}}', date)

        super().__init__('POST', url, token, payload)
