import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

#

# use @todo to cause pytest to skip that section
# handy for stubbing things out and then coming back later to finish them.
# @todo is heirarchical, and not sequential. Meaning that
# it will not skip 'peers' of other todos, only children.
todo = pytest.mark.skip(reason='TODO: pending spec')

class FakeRequest():
    #helps us test http
    #tests a mock file
    #this is an output
    #creates a write file
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    #this is not a 'makefile' like in c++ instead it 'makes' a response file
    #this produces a response/body of the http server
    #written by DJ, don't change haha
    #this is inside the fake request
    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes('{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

#cant call the GET, POST, DELETE functions because they ACTUALLY create a database and open up a server, that is why you have to make dummys because you don't actually want to do any of that

#dummy client and dummy server to pass as params
#dummys are a fake version that are never used
#when creating SquirrelServerHandler
#returns a port like the server would
@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

#returns nothing, never gets called
@pytest.fixture
def dummy_server():
    return None

#a patch for mocking the DB initialize 
#patching the squirrel database
#gives nothing
# function - this gets called a lot.
@pytest.fixture
def mock_db_init(mocker):
    return mocker.patch.object(SquirrelDB, '__init__', return_value=None)

#request the squirrels back
#EDIT TO PRODUCE A VALID SQUIRREL
@pytest.fixture
def mock_db_get_squirrels(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])

#By ID, one squirrel. Doesn't care about the state
@pytest.fixture
def mock_db_get_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value='squirrel')

@pytest.fixture
def mock_db_get_squirrel_not_found(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, "getSquirrel", return_value = None)

@pytest.fixture
def mock_db_create_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, "createSquirrel", return_value = None)

@pytest.fixture
def mock_db_update_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, "updateSquirrel", return_value = None)

@pytest.fixture
def mock_db_delete_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, "deleteSquirrel", return_value = None)

# patch SquirrelServerHandler to make our FakeRequest work correctly
#used on every single func
#set the buff size (headers)
#set them right or else
@pytest.fixture(autouse=True)
def patch_wbufsize(mocker):
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')


# Fake Requests
@pytest.fixture
def fake_get_squirrels_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels')

@pytest.fixture
def fake_get_squirrel_by_id_request(mocker):
    return FakeRequest(mocker.Mock(), "GET", "/squirrels/1")

@pytest.fixture
def fake_get_invalid_resource_request(mocker):
    return FakeRequest(mocker.Mock(), "GET", "/invalid")

#does care about the body of the request
@pytest.fixture
def fake_create_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Chippy&size=small')

@pytest.fixture
def fake_post_with_id_request(mocker):
    return FakeRequest(mocker.Mock(), "POST", "/squirrels/1", body="name=Chippy&size=small")

@pytest.fixture
def fake_post_invalid_resource_request(mocker):
    return FakeRequest(mocker.Mock(), "POST", "/invalid", body="name=Chippy&size=small")

@pytest.fixture
def fake_update_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name=Updated&size=large')

@pytest.fixture
def fake_put_no_id_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrels', body='name=Updated&size=large')

@pytest.fixture
def fake_put_invalid_resource_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/invalid/1', body='name=Updated&size=large')

@pytest.fixture
def fake_delete_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

@pytest.fixture
def fake_delete_no_id_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels')

@pytest.fixture
def fake_delete_invalid_resource_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/invalid/1')

#gives code 500
@pytest.fixture
def fake_bad_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Josh&')


#send_response, send_header and end_headers are inherited functions
#from the BaseHTTPRequestHandler. Go look at documentation here:
# https://docs.python.org/3/library/http.server.html
# Seriously. Go look at it. Pay close attention to what wfile is. :o)
# this fixture mocks all of the send____ that we use. 
# It is really just for convenience and cleanliness of code.
@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers

@pytest.fixture
def mock_handle404(mocker):
    return mocker.patch.object(SquirrelServerHandler, "handle404")

#tests begin here. Your tests should look wildly different. 
# you should begin testing where it makes sense to you.

#grouping
def describe_SquirrelServerHandler():

    def describe_retrieve_squirrels_functionality():

        def it_queries_db_for_squirrels(mocker, dummy_client, dummy_server):
            #setup
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])
            fake_get_squirrels_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels')
            
            #do the thing
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            #assert that the thing was done
            mock_get_squirrels.assert_called_once()

            #no tear down because it was already taken care of

        def it_returns_200_status_code(fake_get_squirrels_request, dummy_client, dummy_server, mock_response_methods):
            
            #set up
            # note: this line 'expands' mock_response_methods into its respective parts
            # only mock_send_response is used in this test. 
            #put into a list
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                 
            # do the thing.
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            
            # assert methods calls and arguments
            mock_send_response.assert_called_once_with(200)

        #look at these examples. They use fixtures. What fixtures should you use?
        def it_sends_json_content_type_header(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()


        # Note that we're doing something with the response from the
        # SquirrelServerHandler in this test. 
        # wfile is the object used to write back the HTTP response from the server.
        # here, we're asserting that it is getting called and being passed the json 
        # response that we mocked in the mock_db_get_squirrels patch.

        def it_returns_response_body_with_squirrels_json_data(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels):
            #Setup: no more setup necessary. all the fixtures solve the setup problem
            #note that mock_db_get_squirrels is passed in. Take that out of the parameters 
            #and run the test again - by passing the fixture - the patch gets done...
            #Do The thing:
            response = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            #assert that the write function was called with a json version of the text 'squirrel'
            # why that? look again at mock_db_get_squirrels
            response.wfile.write.assert_called_once_with(bytes(json.dumps(['squirrel']), "utf-8"))

    def describe_retrieve_single_squirrel_functionality():

        def it_queries_db_for_squirrel_by_id(mocker, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Chippy', 'size': 'small'})
            fake_get_squirrel_by_id_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels/1')
            
            SquirrelServerHandler(fake_get_squirrel_by_id_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_returns_200_status_code_when_squirrel_found(fake_get_squirrel_by_id_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrel_by_id_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(200)

        def it_sends_json_content_type_header_when_squirrel_found(fake_get_squirrel_by_id_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrel_by_id_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_handle404_when_squirrel_not_found(fake_get_squirrel_by_id_request, dummy_client, dummy_server, mock_db_get_squirrel_not_found, mock_handle404):
            SquirrelServerHandler(fake_get_squirrel_by_id_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_get_invalid_resource():

        def it_calls_handle404_for_invalid_resource(fake_get_invalid_resource_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_get_invalid_resource_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_create_squirrels():

        def it_queries_db_to_create_squirrel_with_given_data_attributes(mocker, fake_create_squirrel_request, dummy_client, dummy_server):
            #setup.
            #patch createSquirrel
            mock_db_create_squirrel = mocker.patch.object(SquirrelDB,'createSquirrel',return_value=None)

            #do the thing.
            SquirrelServerHandler(fake_create_squirrel_request,dummy_client,dummy_server)

            #assert the thing was done.
            mock_db_create_squirrel.assert_called_once_with('Chippy','small')

        def it_returns_201_status_code(fake_create_squirrel_request, dummy_client, dummy_server, mock_db_create_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(201)

        def it_calls_end_headers(fake_create_squirrel_request, dummy_client, dummy_server, mock_db_create_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

    def describe_post_with_id():

        def it_calls_handle404_for_post_with_id(fake_post_with_id_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_post_with_id_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_post_invalid_resource():

        def it_calls_handle404_for_invalid_resource(fake_post_invalid_resource_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_post_invalid_resource_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_update_squirrels():

        def it_queries_db_for_squirrel_before_update(mocker, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Chippy', 'size': 'small'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            fake_update_squirrel_request = FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name=Updated&size=large')

            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_updates_squirrel_when_found(mocker, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Chippy', 'size': 'small'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            fake_update_squirrel_request = FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name=Updated&size=large')

            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_update_squirrel.assert_called_once_with('1', 'Updated', 'large')

        def it_returns_204_status_code_when_squirrel_updated(fake_update_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_db_update_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(204)

        def it_calls_end_headers_when_squirrel_updated(fake_update_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_db_update_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_calls_handle404_when_squirrel_not_found_for_update(fake_update_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel_not_found, mock_handle404):
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_put_without_id():

        def it_calls_handle404_for_put_without_id(fake_put_no_id_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_put_no_id_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_put_invalid_resource():

        def it_calls_handle404_for_invalid_resource(fake_put_invalid_resource_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_put_invalid_resource_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_delete_squirrels():

        def it_queries_db_for_squirrel_before_delete(mocker, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Chippy', 'size': 'small'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            fake_delete_squirrel_request = FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_deletes_squirrel_when_found(mocker, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Chippy', 'size': 'small'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            fake_delete_squirrel_request = FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_delete_squirrel.assert_called_once_with('1')

        def it_returns_204_status_code_when_squirrel_deleted(fake_delete_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_db_delete_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(204)

        def it_calls_end_headers_when_squirrel_deleted(fake_delete_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel, mock_db_delete_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_calls_handle404_when_squirrel_not_found_for_delete(fake_delete_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel_not_found, mock_handle404):
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_delete_without_id():

        def it_calls_handle404_for_delete_without_id(fake_delete_no_id_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_delete_no_id_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_delete_invalid_resource():

        def it_calls_handle404_for_invalid_resource(fake_delete_invalid_resource_request, dummy_client, dummy_server, mock_handle404):
            SquirrelServerHandler(fake_delete_invalid_resource_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_handle404():

        def it_returns_404_status_code(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            fake_404_request = FakeRequest(mocker.Mock(), 'GET', '/invalid')

            response = SquirrelServerHandler(fake_404_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(404)

        def it_sends_text_plain_content_type_header(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            fake_404_request = FakeRequest(mocker.Mock(), 'GET', '/invalid')

            SquirrelServerHandler(fake_404_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "text/plain")

        def it_calls_end_headers(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            fake_404_request = FakeRequest(mocker.Mock(), 'GET', '/invalid')

            SquirrelServerHandler(fake_404_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_returns_404_not_found_message(mocker, dummy_client, dummy_server):
            fake_404_request = FakeRequest(mocker.Mock(), 'GET', '/invalid')

            response = SquirrelServerHandler(fake_404_request, dummy_client, dummy_server)
            response.wfile.write.assert_called_once_with(bytes("404 Not Found", "utf-8"))
