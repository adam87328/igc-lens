import requests

class MicroserviceInterface():

    XC_METRICS_URL = 'http://127.0.0.1:8081/xcmetrics'
    XC_SCORE_URL = 'http://127.0.0.1:8082/compmetrics'

    def xc_metrics_service(self,igc_file):
        return self.send_file_to_microservice(igc_file,self.XC_METRICS_URL)

    def xc_score_service(self,igc_file):
        return self.send_file_to_microservice(igc_file,self.XC_SCORE_URL)

    @staticmethod
    def send_file_to_microservice(igc_file,service_url):
        """POSTs a file to specified URL, returns JSON response"""
        # open in binary mode, also does seek(0)
        igc_file.open('rb')
        # Send the file to the microservice
        response = requests.post(
            service_url,
            files={'file': igc_file}
        )
        igc_file.close()
        if not response.status_code == 200:
            raise Exception("microservice response: %d %s" % (
                response.status_code, 
                response.text))
        # parse JSON response
        json_data = response.json()
        # todo: validate JSON
        return json_data

    def are_services_up(self):
        return (self.service_up_xc_score() 
                & self.service_up_xc_metrics())

    def service_up_xc_metrics(self):
        """Test microservice is running, and responds to dummy GET"""
        try:
            response = requests.get(self.XC_METRICS_URL)
        except Exception as e:
            return False
        return response.status_code == 200

    def service_up_xc_score(self):
        """Test microservice is running, and responds to dummy GET"""
        try:
            response = requests.get(self.XC_SCORE_URL)
        except Exception as e:
            return False
        return response.status_code == 200