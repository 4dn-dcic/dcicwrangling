'''
Common functions for GEO Minimization of the JSON objects
'''
URL = 'https://data.4dnucleome.org'


def num2str(value):
    '''transform number to string'''
    if isinstance(value, (int, float)):
        return str(value)
    else:
        return value


def add_to_output_dict(key, value, output_dictionary):
    '''add to the output_dictionary either a single key:value pair or
    all the key:values if value is a dictionary'''
    if isinstance(value, dict):
        for inner_key, inner_value in value.items():
            if inner_value:  # skip if None
                output_dictionary[inner_key] = num2str(inner_value)
    else:
        if value:  # skip if None
            output_dictionary[key] = num2str(value)
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


def boildown_experiments_in_set(experiments_in_set):
    '''Extract list of Experiments with replicate information and experiment
    type(s). This works both for replicate or custom sets.'''
    output_dict = {}
    replicates = []
    exp_ids = []
    exp_types = []
    for exp in experiments_in_set:
        replicates.append({
            'replicate': exp['accession'],
            # get rep num form the first raw file's track_and_facet_info
            'replicate_number': exp['files'][0]['track_and_facet_info'].get('replicate_info', '')
        })
        exp_ids.append(exp['@id'])
        exp_types.append(exp['experiment_type']['display_title'])

    # Replicates
    output_dict['replicate_exps'] = replicates

    # Experiment Type
    unique_exp_types = list(set(exp_types))
    output_dict['experiment_type'] = ', '.join(unique_exp_types)

    return output_dict, exp_ids


def get_series_title(experiment_set):
    '''Generates the series_title field for the ExpSet (replicate or custom)'''
    if experiment_set['experimentset_type'] == 'replicate':
        # Use for ExpSet the exp summary of the first experimental replicate
        exp_summary = experiment_set['experiments_in_set'][0]['display_title'][:-15]
        set_summary = 'Replicate experiments of ' + exp_summary
    elif experiment_set['experimentset_type'] == 'custom':
        # custom sets can have heterogeneous experiments
        # set_summary = experiment_set['description']
        set_summary = experiment_set.get('dataset_label', '') + ' - ' + experiment_set.get('condition', '')
    return experiment_set['accession'] + ' - ' + set_summary


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


def boildown_experiment_type(experiment_type):
    '''Returns experiment_type, library_strategy and data_processing'''
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
        'IP-based 3C': 'ChIA-PET',
        'ATAC-seq': 'ATAC-Seq',
        'ChIP-seq': 'ChIP-Seq',
        'RNA-seq': 'RNA-Seq',
    }
    if experiment_type['assay_subclass_short'] in assay_mapping:
        exp_type_dict['library_strategy'] = assay_mapping[experiment_type['assay_subclass_short']]
    elif exp_type in assay_mapping:
        exp_type_dict['library_strategy'] = assay_mapping[exp_type]
    else:
        exp_type_dict['library_strategy'] = 'OTHER'
    # Data processing
    pipeline = exp2pipeline.get(exp_type)
    if pipeline:
        pipeline_doc = pipeline_pages.get(pipeline)
        if pipeline_doc:
            exp_type_dict['data_processing'] = URL + '/resources/data-analysis/' + pipeline_doc
        else:
            print('WARNING: missing {} documentation page'.format(pipeline))
    return exp_type_dict


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


file_simple_values = [
    'paired_end',  # raw_file
    'accession',
    'description',  # can include data_processing if not 4DN standard pipeline
    'display_title',  # raw_file
    'file_type',
    # 'file_type_detailed',  # has also file_format['display_title']
    'file_classification',
    'instrument',  # raw_file
    'genome_assembly',
    'md5sum',  # raw_file
]

file_function_dispatch = {
    'file_format': boildown_title,
    'related_files': boildown_related_files,
    'quality_metric': boildown_quality_metric,
    'workflow_run_outputs': boildown_wfr_outputs,
}


def boildown_file(file_object):
    '''Works with raw and processed files'''
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
