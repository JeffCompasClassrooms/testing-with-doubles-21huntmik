import pytest
import os.path
import pickle
from unittest.mock import mock_open
from mydb import MyDB

def describe_MyDB():

    @pytest.fixture
    def mock_os_path(mocker):
        return mocker.patch("os.path.isfile")

    @pytest.fixture
    def mock_open_file(mocker):
        return mocker.patch("builtins.open", mock_open())

    @pytest.fixture
    def mock_pickle_load(mocker):
        return mocker.patch("pickle.load")

    @pytest.fixture
    def mock_pickle_dump(mocker):
        return mocker.patch("pickle.dump")

    @pytest.fixture
    def sample_filename():
        return "test_database.pkl"

    @pytest.fixture
    def sample_strings():
        return ["hello", "world", "test"]

    def describe_init_method():
        def test_init_when_file_exists(mocker, mock_os_path, sample_filename):
            mock_os_path.return_value = True
            mock_save_strings = mocker.patch.object(MyDB, "saveStrings")

            db = MyDB(sample_filename)

            assert db.fname == sample_filename
            mock_os_path.assert_called_once_with(sample_filename)
            mock_save_strings.assert_not_called()

        def test_init_when_file_does_not_exist(mocker, mock_os_path, sample_filename):
            mock_os_path.return_value = False
            mock_save_strings = mocker.patch.object(MyDB, "saveStrings")

            db = MyDB(sample_filename)

            assert db.fname == sample_filename
            mock_os_path.assert_called_once_with(sample_filename)
            mock_save_strings.assert_called_once_with([])

    def describe_load_strings_method():

        def test_load_strings_opens_file_correctly(mocker, mock_open_file, mock_pickle_load, sample_filename, sample_strings):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            mock_pickle_load.return_value = sample_strings

            db = MyDB(sample_filename)

            result = db.loadStrings()

            mock_open_file.assert_called_once_with(sample_filename, "rb")
            mock_pickle_load.assert_called_once()
            assert result == sample_strings

        def test_load_strings_with_context_manager(mocker, sample_filename, sample_strings):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            mock_file_handle = mock_open(read_data = b"fake_pickle_data")
            mock_open_func = mocker.patch("builtins.open", mock_file_handle)
            mock_pickle_load = mocker.patch("pickle.load", return_value = sample_strings)

            db = MyDB(sample_filename)

            result = db.loadStrings()

            mock_open_func.assert_called_once_with(sample_filename, "rb")
            mock_file_handle().__enter__.assert_called_once()
            mock_file_handle().__exit__.assert_called_once()
            mock_pickle_load.assert_called_once()
            assert result == sample_strings

    def describe_save_strings_method():

        def test_save_strings_opens_file_correctly(mocker, mock_open_file, mock_pickle_dump, sample_filename, sample_strings):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)

            db = MyDB(sample_filename)

            db.saveStrings(sample_strings)

            mock_open_file.assert_called_with(sample_filename, "wb")
            mock_pickle_dump.assert_called_once()

        def test_save_strings_with_context_manager(mocker, sample_filename, sample_strings):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            mock_file_handle = mock_open()
            mock_open_func = mocker.patch("builtins.open", mock_file_handle)
            mock_pickle_dump = mocker.patch("pickle.dump")

            db = MyDB(sample_filename)

            db.saveStrings(sample_strings)

            mock_open_func.assert_called_with(sample_filename, "wb")
            mock_file_handle().__enter__.assert_called_once()
            mock_file_handle().__exit__.assert_called_once()
            mock_pickle_dump.assert_called_once_with(sample_strings, mock_file_handle().__enter__())

        def test_save_strings_calls_pickle_dump_with_correct_args(mocker, sample_filename, sample_strings):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            mock_file_handle = mock_open()
            mocker.patch("builtins.open", mock_file_handle)
            mock_pickle_dump = mocker.patch("pickle.dump")

            db = MyDB(sample_filename)

            db.saveStrings(sample_strings)

            call_args = mock_pickle_dump.call_args
            assert call_args[0][0] == sample_strings
            assert call_args[0][1] == mock_file_handle().__enter__()

    def describe_save_string_method():

        def test_save_string_loads_existing_data(mocker, sample_filename):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            existing_strings = ["existing1", "existing2"]
            mock_load_strings = mocker.patch.object(MyDB, "loadStrings", return_value = existing_strings)
            mock_save_strings = mocker.patch.object(MyDB, "saveStrings")

            db = MyDB(sample_filename)
            new_string = "new_string"

            db.saveString(new_string)

            mock_load_strings.assert_called_once()


        def test_save_string_appends_and_saves(mocker, sample_filename):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            existing_strings = ["existing1", "existing2"]
            mock_load_strings = mocker.patch.object(MyDB, "loadStrings", return_value = existing_strings.copy())
            mock_save_strings = mocker.patch.object(MyDB, "saveStrings")

            db = MyDB(sample_filename)
            new_string = "new_string"
            expected_strings = ["existing1", "existing2", "new_string"]

            db.saveString(new_string)

            mock_load_strings.assert_called_once()
            mock_save_strings.assert_called_once_with(expected_strings)

        def test_save_string_integration_with_empty_list(mocker, sample_filename):
            mock_os_path = mocker.patch("os.path.isfile", return_value = True)
            mock_load_strings = mocker.patch.object(MyDB, "loadStrings", return_value = [])
            mock_save_strings = mocker.patch.object(MyDB, "saveStrings")

            db = MyDB(sample_filename)
            new_string = "first_string"

            db.saveString(new_string)

            mock_load_strings.assert_called_once()
            mock_save_strings.assert_called_once_with([new_string])
