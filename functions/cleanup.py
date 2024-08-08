from dcicutils import ff_utils
from datetime import datetime


# function to get workflow_details info from db 
# initial datastructure that is the same as that to get info for foursight is transformed
# into the format used in the cleanup functions
# workflow name, accepted revision numbers (0 if none), accetable run time (hours)
def get_workflow_details(my_auth):
    wf_details = {}
    wf_query = "search/?type=Workflow&tags=current&tags=accepted&field=max_runtime" \
        "&app_name!=No value&app_version!=No value&field=app_name&field=app_version"
    workflows = ff_utils.search_metadata(wf_query, my_auth)
    for wf in workflows:
        app_name = wf.get('app_name')
        app_version = wf.get('app_version')
        run_time = wf.get('max_runtime', 0)
        wf_details.setdefault(app_name, {})
        wf_details[app_name].setdefault('accepted_versions', []).append(app_version)
        wf_details[app_name].setdefault('run_time', run_time)
        # for unexpected case of different wf items with same app_name having
        # different run times - use max value
        if run_time > wf_details[app_name].get('run_time'):
            wf_details[app_name]['run_time'] = run_time
    # here is the transformation
    # workflow_details = []
    # for wfname, wf_info in wf_details.items():
    #    workflow_details.append((wfname, wf_info.get('accepted_versions'), [], wf_info.get('run_time')))
    return [(wfname, wf_details[wfname].get('accepted_versions', []), wf_details[wfname].get('run_time'))
            for wfname in wf_details.keys()]


def fetch_pf_associated(pf_id_or_dict, my_key):
    """Given a file accession, find all related items
    1) QCs
    2) wfr producing the file, and other outputs from the same wfr
    3) wfrs this file went as input, and all files/wfrs/qcs around it
    The returned list might contain duplicates, uuids and display titles for qcs"""
    file_as_list = []
    if isinstance(pf_id_or_dict, dict):
        pf_info = pf_id_or_dict
    else:
        pf_info = ff_utils.get_metadata(pf_id_or_dict, my_key)
    file_as_list.append(pf_info['uuid'])
    if pf_info.get('quality_metric'):
        file_as_list.append(pf_info['quality_metric']['uuid'])
    inp_wfrs = pf_info.get('workflow_run_inputs', [])
    for inp_wfr in inp_wfrs:
        file_as_list.extend(fetch_wfr_associated(inp_wfr['uuid'], my_key))
    out_wfrs = pf_info.get('workflow_run_outputs', [])
    for out_wfr in out_wfrs:
        file_as_list.extend(fetch_wfr_associated(out_wfr['uuid'], my_key))
    return list(set(file_as_list))


def fetch_wfr_associated(wfr_id_or_resp, my_key):
    """Given wfr_uuid, find associated output files and qcs"""
    wfr_as_list = []
    if isinstance(wfr_id_or_resp, dict):
        wfr_info = wfr_id_or_resp
    else:
        wfr_info = ff_utils.get_metadata(wfr_id_or_resp, my_key)
    wfr_as_list.append(wfr_info['uuid'])
    if wfr_info.get('output_files'):
        for o in wfr_info['output_files']:
            if o.get('value'):
                wfr_as_list.append(o['value']['uuid'])
            elif o.get('value_qc'):
                wfr_as_list.append(o['value_qc']['uuid'])
    if wfr_info.get('output_quality_metrics'):
        for qc in wfr_info['output_quality_metrics']:
            if qc.get('value'):
                wfr_as_list.append(qc['value']['uuid'])
    if wfr_info.get('quality_metric'):
        wfr_as_list.append(wfr_info['quality_metric']['uuid'])
    return wfr_as_list


def get_wfr_report(wfrs):
    # for a given list of wfrs, produce a simpler report
    wfr_report = []
    for wfr_data in wfrs:
        wfr_rep = {}
        """For a given workflow_run item, grabs details, uuid, run_status, wfr name, date, and run time"""
        wfr_type, time_info = wfr_data['display_title'].split(' run ')
        # skip all style awsem runs
        try:
            wfr_type_base, wfr_version = wfr_type.strip().split(' ')
        except:
            continue
        time_info = time_info.strip('on').strip()
        try:
            wfr_time = datetime.strptime(time_info, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            wfr_time = datetime.strptime(time_info, '%Y-%m-%d %H:%M:%S')
        run_hours = (datetime.utcnow() - wfr_time).total_seconds() / 3600
        output_files = wfr_data.get('output_files', None)
        output_uuids = []
        qc_uuids = []

        # add wfr qc to the qc list
        if wfr_data.get('quality_metric'):
            qc_uuids.append(wfr_data['quality_metric']['uuid'])

        if output_files:
            for i in output_files:
                if i.get('value', None):
                    output_uuids.append(i['value']['uuid'])
                if i.get('value_qc', None):
                    qc_uuids.append(i['value_qc']['uuid'])

        wfr_rep = {'wfr_uuid': wfr_data['uuid'],
                   'wfr_status': wfr_data['run_status'],
                   'wfr_name': wfr_type_base.strip(),
                   'wfr_version': wfr_version.strip(),
                   'wfr_date': wfr_time,
                   'run_time': run_hours,
                   'status': wfr_data['status'],
                   'outputs': output_uuids,
                   'qcs': qc_uuids}
        wfr_report.append(wfr_rep)
    wfr_report = sorted(wfr_report, key=lambda k: (k['wfr_date'], k['wfr_name']))
    return wfr_report


def delete_wfrs(file_resp, my_key, workflow_details, delete=False, stash=None):
    # file_resp in embedded frame
    # stash: all related wfrs for file_resp
    deleted_wfrs = []  # reports WorkflowRun items deleted by this function
    deleted_files = []  # reports File items deleted by this function because outputs of wfr deleted by this function
    deleted_qc = []  # reports QualityMetric items deleted by this function because linked to wfr deleted by this function
    wfr_report = []
    file_type = file_resp['@id'].split('/')[1]
    # special clause until we sort input_wfr_switch issue
    # do not delete output wfrs of control files
    output_wfrs = file_resp.get('workflow_run_outputs')
    if not output_wfrs:
        if file_type == 'files-processed':
            # user submtted processed files
            return
        else:
            # raw files:
            pass
    else:
        output_wfr = output_wfrs[0]
        wfr_type, _ = output_wfr['display_title'].split(' run ')
        if wfr_type in ['encode-chipseq-aln-ctl 1.1.1', 'encode-chipseq-aln-ctl 2.1.6'] :
            print('skipping control file for wfr check', file_resp['accession'])
            return

    wfr_uuids = [i['uuid'] for i in file_resp.get('workflow_run_inputs')]
    wfrs = []
    if wfr_uuids:
        # fetch them from stash
        if stash:
            wfrs = [i for i in stash if i['uuid'] in wfr_uuids]
            assert len(wfrs) == len(wfr_uuids)
        # if no stash, get from database
        else:
            wfrs = [i['embedded'] for i in ff_utils.get_es_metadata(wfr_uuids, sources=['embedded.*'], key=my_key)]
    # look for md5s on files without wfr_run_output (file_microscopy ...)
    else:
        if file_type not in ['files-fastq', 'files-processed']:
            wfrs_url = ('/search/?type=WorkflowRun&type=WorkflowRun&workflow.title=md5+0.2.6&workflow.title=md5+0.0.4'
                        '&input_files.value.accession=') + file_resp['accession']
            wfrs = ff_utils.search_metadata(wfrs_url, key=my_key)
    # Skip sbg and file provenance
    wfrs = [i for i in wfrs if not i['@id'].startswith('/workflow-runs-sbg/')]
    wfrs = [i for i in wfrs if not i['display_title'].startswith('File Provenance Tracking')]

    def _delete_action(wfr_to_del):
        # delete the Workflow Run
        patch_data = {'description': "This workflow run is deleted", 'status': "deleted"}
        deleted_wfrs.append(wfr_to_del['wfr_uuid'])
        ff_utils.patch_metadata(patch_data, obj_id=wfr_to_del['wfr_uuid'], key=my_key)
        # delete output files of the deleted workflow run
        if wfr_to_del['outputs']:
            for out_file_uuid in wfr_to_del['outputs']:
                deleted_files.append(out_file_uuid)
                ff_utils.patch_metadata({'status': "deleted"}, obj_id=out_file_uuid, key=my_key)
        # delete QualityMetric of the deleted workflow run or of the deleted output files
        if wfr_to_del.get('qcs'):
            for out_qc_uuid in wfr_to_del['qcs']:
                deleted_qc.append(out_qc_uuid)
                ff_utils.patch_metadata({'status': "deleted"}, obj_id=out_qc_uuid, key=my_key)
        return

    # CLEAN UP IF FILE IS DELETED
    workflow_names = [wfinfo[0] for wfinfo in workflow_details]
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
            wfr_report = get_wfr_report(wfrs)
            for wfr_to_del in wfr_report:
                if wfr_to_del['uuid'] == '15700187-3843-4062-95ff-57c8ac913a1d':
                    import pdb; pdb.set_trace()
                if wfr_to_del['status'] != 'deleted':
                    if wfr_to_del['wfr_name'] not in workflow_names:
                        print('Unlisted Workflow', wfr_to_del['wfr_name'], 'deleted file workflow',
                              wfr_to_del['wfr_uuid'], file_resp['accession'])
                    ####################################################
                    # TEMPORARY PIECE##################################
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
                        _delete_action(wfr_to_del)

    else:
        # get a report on all workflow_runs
        if not wfrs:
            return
        else:
            wfr_report = get_wfr_report(wfrs)
            # printTable(wfr_report, ['wfr_name', 'run_time', 'wfr_version', 'run_time', 'wfr_status'])
            # check if any unlisted wfr in report
            my_wfr_names = [i['wfr_name'] for i in wfr_report]
            unlisted = [x for x in my_wfr_names if x not in workflow_names]
            # report the unlisted ones
            if unlisted:
                print('Unlisted Workflow', unlisted, 'skipped in', file_resp['accession'])
            for wf_name, accepted_rev, accepted_run_time in workflow_details:
                # for each type of worklow make a list of old ones, and patch status and description
                sub_wfrs = [i for i in wfr_report if i['wfr_name'] == wf_name]
                if sub_wfrs:
                    active_wfr = sub_wfrs[-1]
                    old_wfrs = sub_wfrs[:-1]
                    # check the status of the most recent workflow
                    if active_wfr['wfr_status'] != 'complete':
                        if (active_wfr['wfr_status'] in ['running', 'started'] and active_wfr['run_time'] < accepted_run_time):
                            print(wf_name, 'still running for', file_resp['accession'])
                        else:
                            old_wfrs.append(active_wfr)
                    elif active_wfr['wfr_version'] not in accepted_rev:
                        old_wfrs.append(active_wfr)
                    if old_wfrs:
                        for wfr_to_del in old_wfrs:
                            if wfr_to_del['status'] != 'deleted':
                                if wfr_to_del['status'] in ['archived', 'replaced']:
                                    print(wfr_to_del['wfr_name'], wfr_to_del['status'], ' wfr found, skipping ',
                                          wfr_to_del['wfr_uuid'], file_resp['accession'])
                                    continue
                                ####################################################
                                # TEMPORARY PIECE
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
                                    _delete_action(wfr_to_del)
    deleted_items = deleted_wfrs + deleted_files + deleted_qc
    return deleted_items
