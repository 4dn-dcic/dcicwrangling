from scripts import geo2fdn as geo
from Bio import Entrez
import GEOparse
import pytest


@pytest.fixture
def srx_file():
    return './test/data_files/SRX3028942.xml'


def test_parse_gsm_with_sra(mocker, srx_file):
    with open(srx_file, 'r') as srx:
        with mocker.patch('Bio.Entrez.efetch', return_value = srx):
            gsm = GEOparse.get_GEO(filepath='./test/data_files/GSM2715320.txt')
            exp = geo.parse_gsm(gsm)
    assert exp.link in srx_file
    assert exp.exptype == 'repliseq'
    assert exp.bs == 'SAMN07405769'
    assert exp.layout == 'single'
    assert exp.instr == 'Ion Torrent Proton'
    assert len(exp.runs) == 1
    assert exp.length == 51


def test_parse_gsm_dbgap(mocker):
    with open('./test/data_files/SRX3028942.xml', 'r') as srx:
        with mocker.patch('Bio.Entrez.efetch', return_value = srx):
            gsm = GEOparse.get_GEO(filepath='./test/data_files/GSM2254215.txt')
            exp = geo.parse_gsm(gsm)
    assert exp.bs == 'SAMN05449633'
    assert not exp.layout
    assert exp.instr == 'Illumina HiSeq 2500'
    assert exp.exptype.startswith('hic')
    assert not exp.link
    assert not exp.runs
    assert not exp.length

# test gsm parse with different experiment types autodetected
    # mock get_sra
    # ['dnase hic', 'rnaseq', 'tsaseq', 'chipseq', 'capturec',
    #    'atacseq', 'damid', 'damidseq', 'chiapet']
    # multiple functions or all one function?

def gsm_soft_to_exp_obj(mocker, gsm_file, exp_type=None):
    with mocker.patch('scripts.geo2fdn.Experiment.get_sra'):
        gsm = GEOparse.get_GEO(filepath=gsm_file)
        return geo.parse_gsm(gsm, experiment_type=exp_type)


def test_parse_gsm_sprite(mocker):
    sprite = gsm_soft_to_exp_obj(mocker, './test/data_files/GSM3154187.txt')
    assert sprite.exptype == 'dna sprite'

def test_parse_gsm_capturec():
    pass


def test_parse_gsm_atacseq():
    pass


def test_parse_gsm_damid():
    pass


def test_parse_gsm_chiapet():
    pass


def test_parse_bs_record(mocker):
    with open('./test/data_files/SAMN06219555.xml', 'r') as samn:
        with mocker.patch('Bio.Entrez.efetch', return_value = samn):
            bs = geo.parse_bs_record('SAMN06219555')
    for item in ['tamoxifen', 'liver', 'NIPBL', 'Nipbl(flox/flox)']:
        assert item in bs.description


def test_get_geo_metadata_seq(mocker):
    with mocker.patch('scripts.geo2fdn.Experiment.get_sra'):
        with mocker.patch('scripts.geo2fdn.parse_bs_record', return_value = 'SAMNXXXXXXXX'):
            gse = geo.get_geo_metadata('GSE93431', filepath='./test/data_files/GSE93431_family.soft.gz')
    assert len([exp for exp in gse.experiments if exp.exptype == 'hic']) == 6
    assert len([exp for exp in gse.experiments if exp.exptype == 'chipseq']) == 14
    assert len([exp for exp in gse.experiments if exp.exptype == 'rnaseq']) == 12
    assert len([bs for bs in gse.biosamples]) == 32


def test_get_geo_metadata_microarray(capfd):
    gse = geo.get_geo_metadata('GSE102960', filepath='./test/data_files/GSE102960_family.soft.gz')
    out, err = capfd.readouterr()
    assert not gse
    assert out == 'Sequencing experiments not found. Exiting.\n'


# def test_modify_xls(mocker):
#     with mocker.patch('scripts.geo2fdn.Experiment.get_sra'):

    # input blank excel
    # create dataset
    # save excel
    # compare saved excel to data_file excel
    # delete saved excel
    # modify original function to return outbook rather than save to file?

# modify_xls test with experiment_type
#     exp = gsm_soft_to_exp_obj('./test/data_files/GSM2648491.txt')
# above: unparsable captureC experiment


# experiment_type_compare tests?

def test_experiment_type_compare_sheet_noexp():
    pass


def test_experiment_type_compare_nosheet_exp():
    pass
