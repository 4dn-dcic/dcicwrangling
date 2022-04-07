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
            "wf_uuid": "667b14a7-a47e-4857-adf1-12a6393c4b8e",
            "parameters": {},
            "config": {
                "instance_type": "t2.micro",
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
            "app_name": "insulation-scores-and-boundaries-caller",
            "workflow_uuid": "dc9efc2d-baa5-4304-b72b-14610d8d5fc4",
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
                    'description': 'Boundaries calls on Hi-C contact matrices'}
            }
        },
        {
            "app_name": "compartments-caller",
            "workflow_uuid": "d07fa5d4-8721-403e-89b5-e8f323ac9ece",
            "parameters": {"binsize": 250000, "contact_type": "cis"},
            "config": {'mem': 4, 'cpu': 1, 'ebs_size': '1.1x', 'EBS_optimized': 'false'},
            'custom_pf_fields': {
                'bwfile': {
                    'genome_assembly': genome,
                    'file_type': 'compartments',
                    'description': 'Compartments signals on Hi-C contact matrices'}
            },
        },
        {
            "app_name": "rna-strandedness",
            "workflow_uuid": "af97597e-877a-40b7-b211-98ec0cfb17b4",
            'config': {'mem': 2, 'cpu': 2, "instance_type": "t3.small", 'ebs_size': '1.1x', 'EBS_optimized': 'false'}
        },
        # RNA SEQ
        {
            "app_name": "encode-rnaseq-stranded",
            "workflow_uuid": "4dn-dcic-lab:wf-encode-rnaseq-stranded",
            "parameters": {
                'rna.strandedness': 'stranded',
                'rna.strandedness_direction': '',
                'rna.endedness': ''
            },
            'custom_pf_fields': {
                'rna.outbam': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.plusbw': {
                    'genome_assembly': genome,
                    'file_type': 'read counts (plus)',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.minusbw': {
                    'genome_assembly': genome,
                    'file_type': 'read counts (minus)',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.gene_expression': {
                    'genome_assembly': genome,
                    'file_type': 'gene expression',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.isoform_expression': {
                    'genome_assembly': genome,
                    'file_type': 'isoform expression',
                    'description': 'Output file from RNA seq pipeline'
                }
            }
        },
        {
            "app_name": "encode-rnaseq-unstranded",
            "workflow_uuid": "4dn-dcic-lab:wf-encode-rnaseq-unstranded",
            "parameters": {
                'rna.strandedness': 'unstranded',
                'rna.strandedness_direction': 'unstranded',
                'rna.endedness': 'paired'
            },
            'custom_pf_fields': {
                'rna.outbam': {
                    'genome_assembly': genome,
                    'file_type': 'read positions',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.outbw': {
                    'genome_assembly': genome,
                    'file_type': 'read counts',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.gene_expression': {
                    'genome_assembly': genome,
                    'file_type': 'gene expression',
                    'description': 'Output file from RNA seq pipeline'
                },
                'rna.isoform_expression': {
                    'genome_assembly': genome,
                    'file_type': 'isoform expression',
                    'description': 'Output file from RNA seq pipeline'
                }
            }
        },
        {
            "app_name": "bamqc",
            "workflow_uuid": "42683ab1-59bf-4ec5-a973-030053a134f1",
            "overwrite_input_extra": False,
            "config": {"ebs_size": 10}
        },
        {
            "app_name": "fastq-first-line",
            "workflow_uuid": "93a1a931-d55d-4623-adfb-0fa735daf6ae",
            "overwrite_input_extra": False,
            'config': {'mem': 2, 'cpu': 2, "instance_type": "t3.small"}
        },
        {
            "app_name": "re_checker_workflow",
            "workflow_uuid": "8479d16e-667a-41e9-8ace-391128f50dc5",
            "parameters": {},
            "config": {
                "mem": 4,
                "ebs_size": 10,
                "instance_type": "t3.medium"
            }
        },
        {
            "app_name": "mad_qc_workflow",
            "workflow_uuid": "4dba38f0-af7a-4432-88e4-ca804dea64f8",
            "parameters": {},
            "config": {"ebs_size": 10, "instance_type": "t3.medium"}
        },
        {
            "app_name": "mcoolQC",
            "workflow_uuid": "0bf9f47a-dec1-4324-9b41-fa183880a7db",
            "overwrite_input_extra": False,
            "config": {"ebs_size": 10, "instance_type": "c5ad.2xlarge"}
        },
        # temp
        {
            "app_name": "",
            "workflow_uuid": "",
            "parameters": {},
            'custom_pf_fields': {
                '': {
                    'genome_assembly': genome,
                    'file_type': '',
                    'description': ''}
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
