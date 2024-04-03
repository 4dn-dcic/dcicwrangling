import pytest
from scripts import delete_item_or_fields as diof


def test_diof_get_args_required_default():
    defaults = {
        'dbupdate': False,
        'env': None,
        'key': None,
        'keyfile': 'keypairs.json',
        'search': False,
    }
    args = diof.get_args(['i'])
    for k, v in defaults.items():
        assert getattr(args, k) == v
    assert args.input == ['i']


def test_diof_get_args_missing_required(capsys):
    with pytest.raises(SystemExit) as pe:
        diof.get_args([])
        out = capsys.readouterr()[0]
        assert 'error: the following arguments are required: input' in out
    assert pe.type == SystemExit
    assert pe.value.code == 2


class MockedNamespace(object):
    def __init__(self, dic):
        for k, v in dic.items():
            setattr(self, k, v)


@pytest.fixture
def mocked_args_dbupd_is_false():
    return MockedNamespace(
        {
            'key': None,
            'keyfile': None,
            'env': 'prod',
            'dbupdate': False,
            'search': False,
            'input': ['id1', 'id2'],
            'fields': None
        }
    )


@pytest.fixture
def mocked_args_dbupd_is_true():
    return MockedNamespace(
        {
            'key': None,
            'keyfile': None,
            'env': 'prod',
            'dbupdate': True,
            'search': False,
            'input': ['id1', 'id2'],
            'fields': None
        }
    )


@pytest.fixture
def mocked_args_w_fields_dry_run():
    return MockedNamespace(
        {
            'key': None,
            'keyfile': None,
            'env': 'prod',
            'dbupdate': False,
            'search': False,
            'input': ['id1', 'id2'],
            'fields': ['aliases'],
        }
    )


@pytest.fixture
def mocked_args_w_fields_dbudate():
    return MockedNamespace(
        {
            'key': None,
            'keyfile': None,
            'env': 'prod',
            'dbupdate': True,
            'search': False,
            'input': ['id1', 'id2'],
            'fields': ['aliases'],
        }
    )
def test_diof_main_dryrun_no_fields(mocker, capsys, mocked_args_dbupd_is_false, auth):
    iids = ['id1', 'id2']
    mocker.patch('scripts.delete_item_or_fields.get_args', return_value=mocked_args_dbupd_is_false)
    mocker.patch('scripts.delete_item_or_fields.scu.authenticate', return_value=auth)
    mocker.patch('scripts.delete_item_or_fields.scu.get_item_ids_from_args', return_value=iids)
    mocker.patch('scripts.delete_item_or_fields.get_metadata', side_effect=[None, None])
    diof.main()
    out = capsys.readouterr()[0]
    for i in iids:
        s = "Will set status of %s to DELETED\nDRY RUN" % i
        assert s in out


def test_diof_main_dryrun_w_fields(mocker, capsys, mocked_args_w_fields_dry_run, auth):
    iids = ['id1', 'id2']
    mocker.patch('scripts.delete_item_or_fields.get_args', return_value=mocked_args_w_fields_dry_run)
    mocker.patch('scripts.delete_item_or_fields.scu.authenticate', return_value=auth)
    mocker.patch('scripts.delete_item_or_fields.scu.get_item_ids_from_args', return_value=iids)
    mocker.patch('scripts.delete_item_or_fields.get_metadata', side_effect=[None, None])
    diof.main()
    out = capsys.readouterr()[0]
    for i in iids:
        s = "Will delete aliases from %s\nDRY RUN" % i
        assert s in out


def test_diof_main_dbupdate_delstatus_items(mocker, capsys, mocked_args_dbupd_is_true, auth):
    iids = ['id1', 'id2']
    resp1 = {'status': 'success'}
    resp2 = {'status': 'error', 'description': "access denied"}
    mocker.patch('scripts.delete_item_or_fields.get_args', return_value=mocked_args_dbupd_is_true)
    mocker.patch('scripts.delete_item_or_fields.scu.authenticate', return_value=auth)
    mocker.patch('scripts.delete_item_or_fields.scu.get_item_ids_from_args', return_value=iids)
    mocker.patch('scripts.delete_item_or_fields.get_metadata', side_effect=[None, None])
    mocker.patch('scripts.delete_item_or_fields.delete_metadata', side_effect=[resp1, resp2])
    diof.main()
    out = capsys.readouterr()[0]
    s1 = "Will set status of %s to DELETED\nsuccess" % iids[0]
    s2 = "Will set status of %s to DELETED\n{'status': 'error', 'description': 'access denied'}" %iids[1]
    assert s1 in out
    assert s2 in out


def test_diof_main_dbupdate_delfields(mocker, capsys, mocked_args_w_fields_dbudate, auth):
    iids = ['id1', 'id2']
    resp1 = {'status': 'success'}
    resp2 = {'status': 'error', 'description': "property not found"}
    mocker.patch('scripts.delete_item_or_fields.get_args', return_value=mocked_args_w_fields_dbudate)
    mocker.patch('scripts.delete_item_or_fields.scu.authenticate', return_value=auth)
    mocker.patch('scripts.delete_item_or_fields.scu.get_item_ids_from_args', return_value=iids)
    mocker.patch('scripts.delete_item_or_fields.get_metadata', side_effect=[None, None])
    mocker.patch('scripts.delete_item_or_fields.delete_field', side_effect=[resp1, resp2])
    diof.main()
    out = capsys.readouterr()[0]
    s1 = "Will delete aliases from %s\nsuccess" % iids[0]
    s2 = "Will delete aliases from %s\n{'status': 'error', 'description': 'property not found'}" %iids[1]
    assert s1 in out
    assert s2 in out
