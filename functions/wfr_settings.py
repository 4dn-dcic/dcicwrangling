# Step Settings
def step_settings(step_name, my_organism, attribution, params={}):
    """Return a setting dict for given step, and modify variables in
    output files; genome assembly, file_type, desc, contributing lab."""
    genome = ""
    mapper = {'human': 'GRCh38', 'mouse': 'GRCm38', 'fruit-fly': 'dm6', 'chicken': 'galGal5'}
    genome = mapper.get(my_organism)

    out_n = "This is an output file of the Hi-C processing pipeline"
    int_n = "This is an intermediate file in the HiC processing pipeline"
    out_n_rep = "This is an output file of the RepliSeq processing pipeline"
    # int_n_rep = "This is an intermediate file in the Repliseq processing pipeline"

    wf_dict = [
        {
            'wf_name': 'md5',
            'wf_uuid': 'c77a117b-9a58-477e-aaa5-291a109a99f6',
            'parameters': {}
        },
        {
            'wf_name': 'fastqc-0-11-4-1',
            'wf_uuid': '2324ad76-ff37-4157-8bcc-3ce72b7dace9',
            'parameters': {}
        },
        {
            'wf_name': 'bwa-mem',
            'wf_uuid': '3feedadc-50f9-4bb4-919b-09a8b731d0cc',
            'parameters': {"nThreads": 16},
            'custom_pf_fields': {
                'out_bam': {
                    'genome_assembly': genome,
                    'file_type': 'intermediate file',
                    'description': int_n}
            }
        },
        {
            'wf_name': 'hi-c-processing-bam',
            'wf_uuid': '023bfb3e-9a8b-42b9-a9d4-216079526f68',
            'parameters': {"nthreads_merge": 16, "nthreads_parse_sort": 16},
            'custom_pf_fields': {
                'annotated_bam': {
                    'genome_assembly': genome,
                    'file_type': 'alignment',
                    'description': out_n},
                'filtered_pairs': {
                    'genome_assembly': genome,
                    'file_type': 'contact list-replicate',
                    'description': out_n}
            }
        },
        {
            'wf_name': 'hi-c-processing-pairs',
            'wf_uuid': '4dn-dcic-lab:wf-hi-c-processing-pairs-0.2.7',
            'parameters': {"nthreads": 4,
                           "maxmem": "32g",
                           "max_split_cooler": 10,
                           "no_balance": False
                           },
            'custom_pf_fields': {
                'hic': {
                    'genome_assembly': genome,
                    'file_type': 'contact matrix',
                    'description': out_n},
                'mcool': {
                    'genome_assembly': genome,
                    'file_type': 'contact matrix',
                    'description': out_n},
                'merged_pairs': {
                    'genome_assembly': genome,
                    'file_type': 'contact list-combined',
                    'description': out_n}
            }
        },
        {
            'wf_name': 'repliseq-parta',
            'wf_uuid': '4dn-dcic-lab:wf-repliseq-parta-v16',
            "parameters": {"nthreads": 4, "memperthread": "2G"},
            'custom_pf_fields': {
                'filtered_sorted_deduped_bam': {
                    'genome_assembly': genome,
                    'file_type': 'alignment',
                    'description': out_n_rep},
                'count_bg': {
                    'genome_assembly': genome,
                    'file_type': 'counts',
                    'description': 'read counts per 5 kb bin, unfiltered, unnormalized'}
            }
        },
        {
            "wf_name": "bedGraphToBigWig",
            "wf_uuid": "68d412a1-b78e-4101-b353-2f3da6272529",
            "parameters": {},
            "config": {
                "instance_type": "t3.small",
                "EBS_optimized": False,
                "ebs_size": 10,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "ebs_iops": "",
                "shutdown_min": "now",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "4dn-encode"
            },
            "overwrite_input_extra": False
        },
        {
            "wf_name": "bedtobeddb",
            "wf_uuid": "9d575e99-5ffe-4ea4-b74f-ad40f621cd39",
            "parameters": {},
            "config": {
                "instance_type": "m3.2xlarge",
                "EBS_optimized": False,
                "ebs_size": 10,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "ebs_iops": "",
                "shutdown_min": "now",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "4dn-encode"
            },
            "overwrite_input_extra": False
        },
        {
            "wf_name": "encode-chipseq-aln-chip",
            "wf_uuid": "4dn-dcic-lab:wf-encode-chipseq-aln-chip",
            "parameters": {},
            "config": {
                       "ebs_size": 0,
                       "ebs_type": "gp2",
                       "json_bucket": "4dn-aws-pipeline-run-json",
                       "EBS_optimized": "",
                       "ebs_iops": "",
                       "shutdown_min": "now",
                       "instance_type": "",
                       "password": "",
                       "log_bucket": "tibanna-output",
                       "key_name": "",
                       "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'chip.first_ta': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Positions of aligned reads in bed format, one line per read mate, for control experiment, from ENCODE ChIP-Seq Pipeline'},
                'chip.first_ta_xcor': {
                    'genome_assembly': genome,
                    'file_type': 'intermediate file',
                    'description': 'Counts file used only for QC'}
            }
        },
        {
            "wf_name": "encode-chipseq-aln-ctl",
            "wf_uuid": "4dn-dcic-lab:wf-encode-chipseq-aln-ctl",
            "parameters": {},
            "config": {
                "ebs_size": 0,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "EBS_optimized": "",
                "ebs_iops": "",
                "shutdown_min": 'now',
                "instance_type": "",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "",
                "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'chip.first_ta_ctl': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Positions of aligned reads in bed format, one line per read mate, for control experiment, from ENCODE ChIP-Seq Pipeline'}
            }
        },
        {
            "wf_name": "encode-chipseq-postaln",
            "wf_uuid": "4dn-dcic-lab:wf-encode-chipseq-postaln",
            "parameters": {},
            "config": {
                "ebs_size": 0,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "EBS_optimized": "",
                "ebs_iops": "",
                "shutdown_min": "now",
                "instance_type": "",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "",
                "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'chip.optimal_peak': {
                    'genome_assembly': genome,
                    'file_type': 'peaks',
                    'description': 'Peak calls from ENCODE ChIP-Seq Pipeline'},
                'chip.conservative_peak': {
                    'genome_assembly': genome,
                    'file_type': 'conservative peaks',
                    'description': 'Conservative peak calls from ENCODE ChIP-Seq Pipeline'},
                'chip.sig_fc': {
                    'genome_assembly': genome,
                    'file_type': 'signal fold change',
                    'description': 'ChIP-seq signal fold change over input control'}
            }
        },
        {
            "wf_name": "encode-atacseq-aln",
            "wf_uuid": "4dn-dcic-lab:wf-encode-atacseq-aln",
            "parameters": {},
            "config": {
                "ebs_size": 0,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "EBS_optimized": "",
                "ebs_iops": "",
                "shutdown_min": 'now',
                "instance_type": "",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "",
                "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'atac.first_ta': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Positions of aligned reads in bed format, one line per read mate, from ENCODE ATAC-Seq Pipeline'}
            }
        },
        {
            "wf_name": "encode-atacseq-postaln",
            "wf_uuid": "4dn-dcic-lab:wf-encode-atacseq-postaln",
            "parameters": {},
            "config": {
                "ebs_size": 0,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "EBS_optimized": "",
                "ebs_iops": "",
                "shutdown_min": "now",
                "instance_type": "",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "",
                "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'atac.optimal_peak': {
                    'genome_assembly': genome,
                    'file_type': 'peaks',
                    'description': 'Peak calls from ENCODE ATAC-Seq Pipeline'},
                'atac.conservative_peak': {
                    'genome_assembly': genome,
                    'file_type': 'conservative peaks',
                    'description': 'Conservative peak calls from ENCODE ATAC-Seq Pipeline'},
                'atac.sig_fc': {
                    'genome_assembly': genome,
                    'file_type': 'signal fold change',
                    'description': 'ATAC-seq signal fold change'}
            }
        },
        {
            "wf_name": "mergebed",
            "wf_uuid": "2b10e472-065e-43ed-992c-fccad6417b65",
            "parameters": {"sortv": "0"},
            "config": {
                "ebs_size": 0,
                "ebs_type": "gp2",
                "json_bucket": "4dn-aws-pipeline-run-json",
                "EBS_optimized": "",
                "ebs_iops": "",
                "shutdown_min": "now",
                "instance_type": "",
                "password": "",
                "log_bucket": "tibanna-output",
                "key_name": "",
                "cloudwatch_dashboard": True
            },
            'custom_pf_fields': {
                'merged_bed': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Merged file, positions of aligned reads in bed format, one line per read mate'}
            }
        },
        {
            "wf_name": "insulation-scores-and-boundaries-caller",
            "wf_uuid": "dc9efc2d-baa5-4304-b72b-14610d8d5fc4",
            "parameters": {"binsize": -1, "windowsize": 100000},
            "config": {'mem': 32},
            'custom_pf_fields': {
                'bwfile': {
                    'genome_assembly': genome,
                    'file_type': 'insulation score-diamond',
                    'description': 'Diamond insulation scores calls on Hi-C contact matrices'},
                'bedfile': {
                    'genome_assembly': genome,
                    'file_type': 'boundaries',
                    'description': 'Boundaries calls on Hi-C contact matrices'
                }
            }
        },
        {
            "wf_name": "compartments-caller",
            "wf_uuid": "d07fa5d4-8721-403e-89b5-e8f323ac9ece",
            "parameters": {"binsize": 250000, "contact_type": "cis"},
            "config": {'mem': 4, 'cpu': 1, 'ebs_size': '1.1x', 'EBS_optimized': 'false'},
            'custom_pf_fields': {
                'bwfile': {
                    'genome_assembly': genome,
                    'file_type': 'compartments',
                    'description': 'Compartments signals on Hi-C contact matrices'
                }
            }
        },
        {
            "wf_name": "mcoolQC",
            "wf_uuid": "0bf9f47a-dec1-4324-9b41-fa183880a7db",
            "overwrite_input_extra": False,
            "config": {"ebs_size": 10, "instance_type": "c5ad.2xlarge"}
        },
        {
            "wf_name": "cut_and_run_workflow",
            "wf_uuid": "c5db38be-f139-4157-9832-398bda2c62d2",
            "parameters": {
                "nthreads_trim": 4,
                "nthreads_aln": 4
            },
            "config": {'mem': 8, 'cpu': 4, 'ebs_size': 28},
            "custom_pf_fields": {
                "out_bam": {
                    "genome_assembly": genome,
                    "file_type": "read positions",
                    "description": "Alignment output file from CUT&RUN"
                    },
                "out_bedpe": {
                    "genome_assembly": genome,
                    "file_type": "intermediate file",
                    "description": "Filtered reads, output file from CUT&RUN"
                }
            }
        },
        {
            "wf_name": "cut_and_run_ctl_workflow",
            "wf_uuid": "04895a25-b609-4fc8-b0d5-9dd9e45d9237",
            "parameters": {
                "nthreads_trim": 4,
                "nthreads_aln": 4
            },
            "config": {'mem': 8, 'cpu': 4, 'ebs_size': 20},
            "custom_pf_fields": {
                "out_bam": {
                    "genome_assembly": genome,
                    "file_type": "read positions",
                    "description": "Alignment output file from CUT&RUN",
                    'disable_wfr_inputs': True
                },
                "out_bedpe": {
                    "genome_assembly": genome,
                    "file_type": "intermediate file",
                    "description": "Filtered reads, output file from CUT&RUN",
                    'disable_wfr_inputs': True
                }
            }
        },
        {
            "wf_name": "cut_and_run_peaks",
            "wf_uuid": "b43bcc4e-d566-4fbf-a0bb-375a2ad517d8",
            "config": {'mem': 16, 'cpu': 2, 'ebs_size': 36},
            'custom_pf_fields': {
                "out_bedg": {
                    "genome_assembly": genome,
                    "file_type": "peaks",
                    "description": "Peaks output file from CUT&RUN"
                },
                "out_bw": {
                    "genome_assembly": genome,
                    "file_type": "signal fold change",
                    "description": "Signal track from CUT&RUN"
                }
            }
        }
    ]
    # if params, overwrite parameters
    template = [i for i in wf_dict if i['wf_name'] == step_name][0]
    if params:
        template['parameters'] = params

    if template.get('custom_pf_fields'):
        for a_file in template['custom_pf_fields']:
            template['custom_pf_fields'][a_file].update(attribution)
    template['wfr_meta'] = attribution
    return template
