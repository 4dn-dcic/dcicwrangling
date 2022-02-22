'''
Common functions for GEO Minimization of the JSON objects
'''
URL = 'https://data.4dnucleome.org'


def add_to_output_dict(key, value, output_dictionary):
    '''Add to the output_dictionary either a single key:value pair or
    all the key:values if value is a dictionary.
    If a key is already in the output_dictionary, add value to the existing one
    '''
    def _add_to_output_dict(k, v):
        if v:  # skip if None
            output_dictionary[k] = output_dictionary[k] + v if output_dictionary.get(k) else v
        return
    if isinstance(value, dict):
        for inner_key, inner_value in value.items():
            _add_to_output_dict(inner_key, inner_value)
    else:
        _add_to_output_dict(key, value)
    return output_dictionary


def atid2url(at_id):
    '''replace @id with full URL'''
    return {'url': URL + at_id}


def boildown_title(any_object):
    '''get display_title'''
    return any_object['display_title']


def boildown_list_to_titles(list_of_objects):
    '''get comma-separated list of display_title'''
    return ', '.join([boildown_title(entry) for entry in list_of_objects])


def boildown_protocol(protocol_object):
    '''used for both protocol and document items'''
    protocol_dict = {}
    protocol_simple_interesting_values = ['description', 'url']  # 'protocol_type'
    for key in protocol_object:
        if key == 'attachment':
            protocol_dict['download'] = URL + protocol_object['@id'] + protocol_object['attachment']['href']
        elif key in protocol_simple_interesting_values:
            protocol_dict[key] = protocol_object[key]
    return protocol_dict


def boildown_protocols(protocols):
    '''return list of protocols(dictionaries)'''
    return [boildown_protocol(p) for p in protocols]


def boildown_exp_display_title(display_title):
    '''shorten experiment display title if longer than 120,
    keeping accession at the end'''
    if len(display_title) > 120:
        accession = display_title[-15:]
        display_title = display_title[:102] + '...' + accession
    return display_title


def boildown_award(award_object):
    '''get award number, extracted from the @id'''
    return award_object['@id'].split('/')[2]


def boildown_date_modified(date_modified_object):
    '''get date_modified'''
    return date_modified_object['date_modified'].split('T')[0]


def boildown_external_references(external_references_list):
    '''join list of validated dbxrefs (from which this calcprop derives)'''
    refs = []
    for reference in external_references_list:
        # get ref only if 'uri' was calculated correctly
        if reference.get('uri'):
            refs.append(reference['ref'])
    return ', '.join(refs)


# additional functions for ExpSet
def boildown_publication(publication):
    '''returns a dictionary with one key
    produced_in_pub: PMID if present, otherwise series_citation: display_title'''
    if publication['ID'].split(':')[0] == 'PMID':
        pub = {'produced_in_pub': publication['ID'].split(':')[1]}
    else:
        pub = {'series_citation': publication['display_title']}
    return pub


def get_series_title(experiment_set):
    '''Generates the series_title field for the ExpSet (replicate or custom)'''
    if experiment_set['experimentset_type'] == 'replicate':
        # Use for ExpSet the exp summary of the first experimental replicate
        exp_summary = experiment_set['experiments_in_set'][0]['display_title'][:-15]
        set_summary = ' - ' + 'Replicate experiments of ' + exp_summary
    elif experiment_set['experimentset_type'] == 'custom':
        # custom sets can have heterogeneous experiments
        set_summary = ' - ' + experiment_set['dataset_label'] if experiment_set.get('dataset_label') else ''
        set_summary += ' - ' + experiment_set['condition'] if experiment_set.get('condition') else ''
    return experiment_set['accession'] + set_summary


def boildown_organism(organism_object):
    '''Return interesting organism values from organism_object'''
    organism_dict = {}
    organism_dict['organism_name'] = organism_object['scientific_name']
    organism_dict['organism_id'] = organism_object['taxon_id']
    return organism_dict


# for Experiment
pipeline_pages = {
    'atacseq': 'atacseq-processing-pipeline',
    'chipseq': 'chipseq-processing-pipeline',
    'hic': 'hi_c-processing-pipeline',
    'rnaseq': 'rnaseq-processing-pipeline',
}

exp2pipeline = {
    # official
    'in situ Hi-C': 'hic',
    'Dilution Hi-C': 'hic',
    'TCC': 'hic',
    'DNase Hi-C': 'hic',
    'Capture Hi-C': 'hic',
    'Micro-C': 'hic',
    'ATAC-seq': 'atacseq',
    'ChIP-seq': 'chipseq',
    'RNA-seq': 'rnaseq',
    '2-stage Repli-seq': 'repliseq',
    'Multi-stage Repli-seq': 'repliseq',

    # preliminary
    # 'ChIA-PET': 'hic',
    # 'in situ ChIA-PET': 'hic',
    # 'TrAC-loop': 'hic',
    # 'PLAC-seq': 'hic',
    # 'MARGI': 'margi',
    # 'TSA-seq': 'repliseq',
    # 'NAD-seq': 'repliseq',
}


def data_processing(experiment_object, OVERRIDE_DATA_PROCESSING):
    '''Return a string for data processing. If 4DN pipeline, this is a link to
    the documentation. It can be overridden if needed.'''
    # TODO: If supplementary files are included, automate how lab-provided
    # processing description is reported. Also consider mixed cases, e.g.
    # when both processed files and supplementary files are included.
    if OVERRIDE_DATA_PROCESSING:
        formatted_string = OVERRIDE_DATA_PROCESSING.replace("\n", "!Sample_data_processing = ")
        return formatted_string
    processing = ''
    exp_type = experiment_object['experiment_type']['title']
    pipeline = exp2pipeline.get(exp_type)
    if pipeline:
        pipeline_doc = pipeline_pages.get(pipeline)
        assert (pipeline_doc), 'Missing {} documentation page'.format(pipeline)
        processing = URL + '/resources/data-analysis/' + pipeline_doc
    assert (processing), 'Missing data_processing information'
    return processing


def boildown_experiment_type(experiment_type):
    '''Returns experiment_type and library_strategy'''
    exp_type_dict = {}
    exp_type = experiment_type['title']
    # Experiment type
    exp_type_dict['experiment_type'] = exp_type
    # Library strategy
    assay_mapping = {
        # TODO: This is a controlled vocabulary from GEO. Currently (May 2021)
        # all 4DN experiment types not present in GEO fall in the category
        # "OTHER". Check again in the future in case new experiments are added.
        'Hi-C': 'Hi-C',
        'Hi-C (single cell)': 'Hi-C',
        'IP-based 3C': 'ChIA-PET',
        'ATAC-seq': 'ATAC-Seq',
        'sci-ATAC-seq': 'ATAC-Seq',
        'ChIP-seq': 'ChIP-Seq',
        'RNA-seq': 'RNA-Seq',
        'sci-RNA-seq': 'RNA-Seq',
    }
    if experiment_type['assay_subclass_short'] in assay_mapping:
        exp_type_dict['library_strategy'] = assay_mapping[experiment_type['assay_subclass_short']]
    elif exp_type in assay_mapping:
        exp_type_dict['library_strategy'] = assay_mapping[exp_type]
    else:
        exp_type_dict['library_strategy'] = 'OTHER'
    return exp_type_dict


def boildown_molecule(experiment_object, exported_experiment):
    '''molecule is required in GEO. We have such field but it is often empty.
    There are different options for RNA-seq, while for other experiment types
    it is typically "genomic DNA"'''
    if exported_experiment.get('molecule'):
        # molecule already found in the metadata
        molecule = exported_experiment['molecule']
    elif exported_experiment['library_strategy'] in ['Hi-C', 'ChIA-PET', 'ATAC-Seq', 'ChIP-Seq']:
        molecule = 'genomic DNA'
    elif exported_experiment['library_strategy'] in ['RNA-Seq', 'OTHER']:  # # TODO: this should be refined
        raise Exception('Specify which molecule is sequenced in the Experiment metadata')
    return molecule


def boildown_exp_categorizer(exp_categorizer_object):
    '''This is a calcprop for all experiments'''
    output = exp_categorizer_object.get('combined', '')
    return output


def boildown_experiment_relations(experiment_relations):
    relations = []
    for rel in experiment_relations:
        rel_type = rel['relationship_type']
        rel_item = rel['experiment']['@id'].split('/')[2]
        relations.append(rel_type + ": " + rel_item)
    return ', '.join(relations)


def boildown_biosample_name(biosample):
    return biosample['accession'], biosample['@id']


def boildown_biosample_quantity(experiment_object):
    unit = experiment_object.get('biosample_quantity_units', '')
    quantity = experiment_object.get('biosample_quantity', '')
    if unit == 'cells':
        quantity = str(int(quantity))
    else:
        quantity = str(quantity)
    return quantity + ' ' + unit


def boildown_targeted_regions(targeted_regions):
    '''Specific to Capture Hi-C Experiments. Ignores oligo_file'''
    targets = []
    for region in targeted_regions:
        targets.append(boildown_title(region['target']))
    return ', '.join(targets)


def boildown_tissue_organ_info(tissue_organ_info):
    # only extract tissue, ignoring organ_system terms
    # this calc prop searches tissue in different places and also deals with mixed tissues
    return {'tissue_source': tissue_organ_info.get('tissue_source')}


def boildown_related_files(related_files):
    # keep only "paired with" relationships
    relations = []
    for rel_file in related_files:
        if rel_file['relationship_type'] == "paired with":
            relations.append(rel_file['file']['accession'])
#             relations.append(rel_file['relationship_type'] + " " + rel_file['file']['accession'])
    return ', '.join(relations)


def boildown_quality_metric(quality_metric):
    '''input is only quality_metric embedded in file, not entire object'''
    qc_dict = {}
    for metric, value in quality_metric.items():
        if metric in ['Sequence length', 'Total Sequences']:
            qc_dict[metric] = value
    return qc_dict


def boildown_wfr_outputs(wfr_outputs):
    wfr_dict = {}
    if wfr_outputs:
        wfr = wfr_outputs[0]  # file derives from the first wfr in the list
        wfr_dict['workflow_run'] = URL + wfr['@id']
        # wfr_dict['workflow'] = wfr['workflow']['display_title']
        input_files = [f['value']['display_title'] for f in wfr['input_files']]
        wfr_dict['derived_from'] = ", ".join(input_files)
    return wfr_dict


def validate_instrument_enum(instrument):
    '''Instrument field is an enum on GEO, but not on 4DN. This function checks
    that the value is accepted for GEO submission. In case of errors, check
    on GEO if this list needs to be updated.'''
    instrument_enum = [
        "Illumina Genome Analyzer",
        "Illumina Genome Analyzer II",
        "Illumina Genome Analyzer IIx",
        "Illumina HiSeq 1000",
        "Illumina HiSeq 1500",
        "Illumina HiSeq 2000",
        "Illumina HiSeq 2500",
        "Illumina HiSeq 3000",
        "Illumina HiSeq 4000",
        "Illumina MiSeq",
        "Illumina HiScanSQ",
        "Illumina MiniSeq",
        "Illumina NextSeq 500",
        "Illumina NovaSeq 6000",
        "Illumina iSeq 100",
        "NextSeq 550",
        "NextSeq 1000",
        "NextSeq 2000",
        "HiSeq X Ten",
        "HiSeq X Five",
    ]
    if instrument not in instrument_enum:
        print(f"WARNING: {instrument} Instrument is not one of the enum accepted by GEO")
    return instrument


file_simple_values = [
    'paired_end',  # raw_file
    'accession',
    'description',  # can include data_processing if not 4DN standard pipeline
    'display_title',  # raw_file
    'file_type',
    # 'file_type_detailed',  # has also file_format['display_title']
    'file_classification',
    'genome_assembly',
    'md5sum',  # raw_file
]

file_function_dispatch = {
    'file_format': boildown_title,
    'instrument': validate_instrument_enum,
    'related_files': boildown_related_files,
    'quality_metric': boildown_quality_metric,
    'workflow_run_outputs': boildown_wfr_outputs,
}


def boildown_file(file_object):
    '''Works with raw, processed and reference files'''
    file_dict = {}
    for key, value in file_object.items():
        export_value = None
        if key in file_simple_values:
            export_value = value
        elif key in file_function_dispatch:
            export_value = file_function_dispatch[key](value)
        if export_value:
            file_dict = add_to_output_dict(key, export_value, file_dict)
    return file_dict
