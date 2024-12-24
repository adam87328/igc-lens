import requests
import json

class MicroserviceInterface():

    XCMETRICS_URL = 'http://127.0.0.1:8081/'
    XCSCORE_URL = 'http://127.0.0.1:8083/'
    GEOLOOKUP_URL = 'http://127.0.0.1:8082/'

    def takeoffdb_service(self,lat,lon):
        response = requests.get(
            self.GEOLOOKUP_URL + 'takeoffdb', 
            params={'lat': lat, 'lon': lon} )
        
        return json.loads(response.text)

    def geocode_service(self,lat,lon):
        response = requests.get(
            self.GEOLOOKUP_URL + 'geocode', 
            params={'lat': lat, 'lon': lon} )
        return json.loads(response.text)

    def xcmetrics_service(self,igc_file):
        return self.send_file_to_microservice(igc_file,self.XCMETRICS_URL)

    def xcscore_service(self,igc_file):
        return self.send_file_to_microservice(igc_file,self.XCSCORE_URL)

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
        return (  self.service_up_xcscore() 
                & self.service_up_xcmetrics()
                & self.service_up_geolookup()
                )

    def service_up_xcmetrics(self):
        """Test microservice is running, and responds to dummy GET"""
        try:
            response = requests.get(self.XCMETRICS_URL)
        except Exception as e:
            return False
        return response.status_code == 200

    def service_up_xcscore(self):
        """Test microservice is running, and responds to dummy GET"""
        try:
            response = requests.get(self.XCSCORE_URL)
        except Exception as e:
            return False
        return response.status_code == 200

    def service_up_geolookup(self):
        """Test microservice is running, and responds to dummy GET"""
        try:
            response = requests.get(self.GEOLOOKUP_URL)
        except Exception as e:
            return False
        return response.status_code == 200