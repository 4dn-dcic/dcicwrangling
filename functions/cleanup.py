from dcicutils import ff_utils
import functions.notebook_functions as nb

# what kind of files should be searched for worflow run inputs, use url compatible naming

# accepted workflows
# workflow name, accepted revision numbers (0 if none), accetable run time (hours)
workflow_details = [['md5', ['0.0.4', '0.2.6'], 12],
                    ['fastqc-0-11-4-1', ['0.2.0'], 50],
                    ['bwa-mem', ['0.2.6'], 50],
                    ['pairsqc-single', ['0.2.5', '0.2.6'], 50],
                    ['hi-c-processing-bam', ['0.2.6'], 50],
                    ['hi-c-processing-pairs', ['0.2.6'], 200],
                    ['hi-c-processing-pairs-nore', ['0.2.6'], 200],
                    ['hi-c-processing-pairs-nonorm', ['0.2.6'], 200],
                    ['hi-c-processing-pairs-nore-nonorm', ['0.2.6'], 200],
                    ['repliseq-parta', ['v13.1', 'v14'], 200],
                    ['bedGraphToBigWig', ['v4'], 24],
                    ['bedtobeddb', ['v2'], 24],
                    ['encode-chipseq-aln-chip', ['1.1.1'], 200],
                    ['encode-chipseq-aln-ctl', ['1.1.1'], 200],
                    ['encode-chipseq-postaln', ['1.1.1'], 200],
                    ['encode-atacseq-aln 1.1.1', ['1.1.1'], 200],
                    ['encode-atacseq-postaln', ['1.1.1'], 200],
                    ['mergebed', ['v1'], 200]
                    ]

workflow_names = [i[0] for i in workflow_details]


def delete_wfrs(file_resp, my_key, delete=False):
    # file_resp in object_frame
    deleted_wfrs = []
    wfr_report = []
    # special clause until we sort input_wfr_switch issue
    # do not delete output wfrs of control files
    output_wfrs = file_resp.get('workflow_run_outputs')
    if not output_wfrs:
        pass
    else:
        output_wfr = ff_utils.get_metadata(output_wfrs[0], key=my_key)
        wfr_type, time_info = output_wfr['display_title'].split(' run ')
        if wfr_type == 'encode-chipseq-aln-ctl 1.1.1':
            print('skipping control file for wfr check', file_resp['accession'])
            return

    wfrs = file_resp.get('workflow_run_inputs')
    if wfrs:
        wfrs = [ff_utils.get_metadata(w, key=my_key) for w in wfrs]
    # look for md5s
    # to do add more single input runs
    if not wfrs:
        wfrs_url = ('/search/?type=WorkflowRun&type=WorkflowRun&workflow.title=md5'
                    '&input_files.value.accession=') + file_resp['accession']
        wfrs = ff_utils.search_metadata(wfrs_url, key=my_key)

    # Delete wfrs if file is deleted
    if file_resp['status'] == 'deleted':
        if file_resp.get('quality_metric'):
            if delete:
                qc_uuid = file_resp['quality_metric']['uuid']
                ff_utils.delete_field(file_resp, 'quality_metric', key=my_key)
                # delete quality metrics object
                patch_data = {'status': "deleted"}
                ff_utils.patch_metadata(patch_data, obj_id=qc_uuid, key=my_key)
        # delete all workflows for deleted files
        if not wfrs:
            return
        else:
            wfr_report = nb.get_wfr_report(wfrs, my_key)
            for wfr_to_del in wfr_report:
                if wfr_to_del['status'] != 'deleted':
                    if wfr_to_del['wfr_name'] not in workflow_names:
                        print('Unlisted Workflow', wfr_to_del['wfr_name'], 'deleted file workflow',
                              wfr_to_del['wfr_uuid'], file_resp['accession'])
                    ####################################################
                    ## TEMPORARY PIECE##################################
                    if wfr_to_del['status'] == 'released to project':
                        print('saved from deletion', wfr_to_del['wfr_name'], 'deleted file workflow',
                              wfr_to_del['wfr_uuid'], file_resp['accession'])
                        return
                    if wfr_to_del['status'] == 'released':
                        print('delete released!!!!!', wfr_to_del['wfr_name'], 'deleted file workflow',
                              wfr_to_del['wfr_uuid'], file_resp['accession'])
                        return
                    #####################################################
                    print(wfr_to_del['wfr_name'], 'deleted file workflow', wfr_to_del['wfr_uuid'], file_resp['accession'])
                    if delete:
                        patch_data = {'description': "This workflow run is deleted", 'status': "deleted"}
                        deleted_wfrs.append(wfr_to_del['wfr_uuid'])
                        ff_utils.patch_metadata(patch_data, obj_id=wfr_to_del['wfr_uuid'], key=my_key)
                        # delete output files of the deleted workflow run
                        if wfr_to_del['outputs']:
                            for out_file in wfr_to_del['outputs']:
                                ff_utils.patch_metadata({'status': "deleted"}, obj_id=out_file, key=my_key)

    else:
        # get a report on all workflow_runs
        if not wfrs:
            return
        else:
            wfr_report = nb.get_wfr_report(wfrs, my_key)
            # printTable(wfr_report, ['wfr_name', 'run_time', 'wfr_version', 'run_time', 'wfr_status'])
            # check if any unlisted wfr in report
            my_wfr_names = [i['wfr_name'] for i in wfr_report]
            unlisted = [x for x in my_wfr_names if x not in workflow_names]
            #report the unlisted ones
            if unlisted:
                print('Unlisted Workflow', unlisted, 'skipped in', file_resp['accession'])
            for wf_name, accepted_rev, accepted_run_time in workflow_details:
                #for each type of worklow make a list of old ones, and patch status and description
                sub_wfrs = [i for i in wfr_report if i['wfr_name'] == wf_name]
                if sub_wfrs:
                    active_wfr = sub_wfrs[-1]
                    old_wfrs = sub_wfrs[:-1]
                    # check the status of the most recent workflow
                    if active_wfr['wfr_status'] != 'complete':
                        if (
                            active_wfr['wfr_status'] in ['running', 'started']
                            and active_wfr['run_time'] < accepted_run_time
                        ):
                            print(wf_name, 'still running for', file_resp['accession'])
                        else:
                            old_wfrs.append(active_wfr)
                    elif active_wfr['wfr_version'] not in accepted_rev:
                        old_wfrs.append(active_wfr)
                    if old_wfrs:
                        for wfr_to_del in old_wfrs:
                            if wfr_to_del['status'] != 'deleted':
                                if wfr_to_del['status'] in ['archived', 'replaced']:
                                    print(wfr_to_del['wfr_name'], wfr_to_del['status'], ' wfr found, skipping ', wfr_to_del['wfr_uuid'], file_resp['accession'])
                                    continue
                                ####################################################
                                ## TEMPORARY PIECE
                                if wfr_to_del['status'] == 'released to project':
                                    print('saved from deletion', wfr_to_del['wfr_name'], 'old style or dub',
                                          wfr_to_del['wfr_uuid'], file_resp['accession'])
                                    continue
                                if wfr_to_del['status'] == 'released':
                                    print('delete released????', wfr_to_del['wfr_name'], 'old style or dub',
                                          wfr_to_del['wfr_uuid'], file_resp['accession'])
                                    continue
                                ####################################################

                                print(wfr_to_del['wfr_name'], 'old style or dub',
                                      wfr_to_del['wfr_uuid'], file_resp['accession'])
                                if delete:
                                    patch_data = {'description': "This workflow run is deleted", 'status': "deleted"}
                                    deleted_wfrs.append(wfr_to_del['wfr_uuid'])
                                    ff_utils.patch_metadata(patch_data, obj_id=wfr_to_del['wfr_uuid'], key=my_key)
                                    # delete output files of the deleted workflow run
                                    if wfr_to_del['outputs']:
                                        for out_file in wfr_to_del['outputs']:
                                            ff_utils.patch_metadata({'status': "deleted"}, obj_id=out_file, key=my_key)
    return deleted_wfrs
