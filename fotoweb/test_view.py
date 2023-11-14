import os
import json
from unittest import TestCase, mock
from django.test import RequestFactory
from rest_framework.response import Response
from myapp.views import maketitle

class MakeTitleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.description = "A beautiful sunset over the mountains"
        self.keywords = "sunset, mountains, nature"
        self.request_data = {
            "description": self.description,
            "keywords": self.keywords
        }

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    @mock.patch('requests.post')
    def test_maketitle(self, mock_post):
        # Mock response from OpenAI API
        mock_response_data = {
            "choices": [
                {"message": {"content": "A stunning sunset behind majestic mountains"}},
                {"message": {"content": "An awe-inspiring view of the mountains at sunset"}},
                {"message": {"content": "Captivating beauty of the sunset over the mountains"}},
                {"message": {"content": "The breathtaking colors of a sunset over the mountains"}},
                {"message": {"content": "Experience the serenity of a mountain sunset"}}
            ],
            "usage": {"prompt_tokens": 182, "completion_tokens": 31, "total_tokens": 213}
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(mock_response_data)
        mock_post.return_value = mock_response

        # Create a request object with request data
        request = self.factory.post('/maketitle', data=self.request_data)

        # Call the view function
        response = maketitle(request)

        # Assert the response
        expected_title = [
            "A stunning sunset behind majestic mountains",
            "An awe-inspiring view of the mountains at sunset",
            "Captivating beauty of the sunset over the mountains",
            "The breathtaking colors of a sunset over the mountains",
            "Experience the serenity of a mountain sunset"
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], expected_title)

        # Assert the API key and headers used in the POST request
        self.assertEqual(mock_post.call_args[0][0], 'https://api.openai.com/v1/chat/completions')
        self.assertEqual(mock_post.call_args[1]['headers'], {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer fake_api_key'
        })

        # Assert the request data payload sent in the POST request
        expected_payload = {
            'model': 'gpt-3.5-turbo-1106',
            'messages': [
                {'role': 'system', 'content': 'You are a curator for microstock photo submission.'},
                {'role': 'user', 'content': f"""Make a caption for the photo with the description and keywords below. 
                No more than 20 words, one sentence. No quotes and no dot at the end.
                Make sure the length of the caption is under 200 characters.\n

                Photo will be submitted to a microstock photo websites - Shutterstock and Adobe stock. 
                Be direct. Put in some emotions, but not too much. Keywords may contain geographical data, use them if you can.
                Don't include keywords in the caption, use them as an additional source of information.
                Description


                ------
                {self.description}
                ------
                Keywords


                ------
                {self.keywords}
                """}
            ],
            'temperature': 1,
            'n': 5
        }
        self.assertEqual(json.loads(mock_post.call_args[1]['data']), expected_payload)
