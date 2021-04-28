'''
Common functions for GEO Minimization of the JSON objects
'''
URL = 'https://data.4dnucleome.org'


def add_to_output_dict(key, value, output_dictionary):
    '''add to the output_dictionary either a single key:value pair or
    all the key:values if value is a dictionary'''
    if isinstance(value, dict):
        for inner_key, inner_value in value.items():
            if inner_value:  # skip if None
                output_dictionary[inner_key] = str(inner_value)
    else:
        if value:  # skip if None
            output_dictionary[key] = str(value)
    return output_dictionary


def boildown_at_id(at_id):
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
def boildown_replicate_exps(replicate_exps):
    '''return list of dict with Exp accession, biorep and techrep'''
    replicates = []
    exp_ids = []
    for replicate in replicate_exps:
        replicates.append({
            'replicate': replicate['replicate_exp']['accession'],
            'biological_replicate_number': replicate['bio_rep_no'],
            'technical_replicate_number': replicate['tec_rep_no']
        })
        exp_ids.append(replicate['replicate_exp']['@id'])
    return replicates, exp_ids


def boildown_publication(publication):
    '''returns a dictionary with one key
    produced_in_pub: PMID if present, otherwise series_citation: display_title'''
    if publication['ID'].split(':')[0] == 'PMID':
        pub = {'produced_in_pub': publication['ID'].split(':')[1]}
    else:
        pub = {'series_citation': publication['display_title']}
    return pub


def boildown_experiments_in_set(experiments_in_set):
    '''extract experiment_type from the first experiment in an ExpSet'''
    output_dict = {}
    experiment = experiments_in_set[0]
    output_dict['experiment_type'] = experiment['experiment_type']['display_title']
    # output_dict['organism_id'] = get_organism_from_experiment(experiment)
    return output_dict


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
    '''returns experiment_type and data_processing'''
    exp_type_dict = {}
    exp_type = experiment_type['title']
    exp_type_dict['experiment_type'] = exp_type
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
