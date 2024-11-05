import requests
from rest_framework import generics, status as drf_status
from rest_framework.response import Response
# lib for reading environment variables
from decouple import config #https://pypi.org/project/python-decouple/

from .models import URL
from .serializers import URLSerializer
# Create your views here.
class URLCreateView(generics.CreateAPIView):
    # queryset = URL.objects.all()
    # serializer_class = URLSerializer

    def post(self, request, *args, **kwargs):
        original_url = request.data.get('original_url')

        if not original_url:
            return Response({'error': 'URL is required.'}, status=drf_status.HTTP_400_BAD_REQUEST)

        #call virusTotal API
        api_key = config('URL_SCAN', default='generic_key')
        url = config('API_KEY_SCAN', default='generic_url')
        headers = {
            'x-apikey': api_key,
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded'
        }
        # encode the url in format that can be sent in the request
        encoded_url = requests.utils.quote(original_url)
        print(encoded_url)
        # send the request to the API and get the response
        response = requests.post(url, headers=headers, data={'url': encoded_url})
        if response.status_code == 200:
            result = response.json()
            print(result)
            analysis_link = result.get('data', {}).get('links', {}).get('self')

            if not analysis_link:
                return Response({'error': 'Analysis link not found in the response.'}, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Make a subsequent request to get the analysis results
            analysis_response = requests.get(analysis_link, headers={'x-apikey': api_key})

            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                print('x------------>',analysis_result)
                data_res = analysis_result.get('data', {}).get('attributes', {})
                status = data_res.get('status', {})
                detection = data_res.get('stats', {})
                # data_res = result.get('data', {}).get('attributes', {})
                # status = data_res.get('last_analysis_stats', {})
                # detection = data_res.get('last_analysis_results', {})
                # Process the result and create a instance of URL model
                url_instance = URL(
                    original_url = original_url,
                    status = status,
                    detection = detection
                )
                # save the instance
                url_instance.save()
                # Process the result and create a response for the frontend.
                data = {
                    'status': status,
                    'url_description': original_url,
                    'detection': detection
                }
                return Response(data, status=drf_status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to retrieve the analysis results.'}, status=analysis_response.status_code)
        else:
            return Response({'error':'Failed to scan the URL.'}, status=response.status_code)