import unittest
from functions import display_userdetails
from mockupdb import go, MockupDB, OpQuery
import json

class functionsTest(unittest.TestCase):
    def setUp(self):
        self.server = MockupDB(auto_ismaster={"maxWireVersion": 3})
        self.server.run()
        #self.testConf['mongo_url'] = 
        self.testConf = {
            "mongo_url" : self.server.uri, 
            "host_url": "https://lmp.nupursjsu.net",
            "host" : "127.0.0.1",
            "port" : 8080
        }

    def tearDown(self):
        self.server.stop()

    def test_display_userdetails(self):
        user_details = {'userId': 'user1', 'firstName': 'myFirstName', 'lastName': 'myLastName', 'age': 20}
        userId = "user1"

        details = go(display_userdetails, userId, self.testConf)
        query = OpQuery({"userId": "user1"}, namespace="Books.myapp_user", fields={"_id": False})
        request = self.server.receives(query)
        request.reply(user_details)

        output = details()
        for key in output:
            if key in user_details:
                self.assertEqual(user_details[key], output[key])

if __name__ == '__main__':
    unittest.main()