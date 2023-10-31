===============
dcicwrangling
===============

----------
Change Log
------

3.0.0
=====

`PR:119 update setting for repliseq v16.1 <https://github.com/4dn-dcic/dcicwrangling/pull/110>_`

* updates to wfr_settings and cleanup utils to support updated v16.1 repliseq


3.0.0
=====

`PR:109 python 3.8-3.11 support <https://github.com/4dn-dcic/dcicwrangling/pull/109>_`

* upgrade to support python versions 3.8 - 3.11

2.4.1
=====

* Fixed 12_geo_submission.ipynb to avoid adding duplicate protocol items in the JSON files specifically for experiments where both 'protocol' and 'protocol_variation' is present

2.4.0
=====

`PR:107 add useful notebook #15 to add opf collections to esets <https://github.com/4dn-dcic/dcicwrangling/pull/107>_`

* added a new useful notebook that allows you to use a lab submitted processed file sheet to link replicate sets to other processed files collections for that set

2.3.0
=====

`PR:106 update get_schemas calls <https://github.com/4dn-dcic/dcicwrangling/pull/106>_`

* update to use get_schemas function from dcicutils rather than having a 'broken' redundant copy
* same for dump_json_data function
* updated notebooks to call dcicutils versions of functions
* simplify get_schemas_names_and_fields to use dcicutil function

2.2.1
=====

* hotfix to update .gitignore to not publish cruft

2.2.0
=====

`PR:105 update dcicutils version <https://github.com/4dn-dcic/dcicwrangling/pull/105>_`

* lock in an update to dcicutils required due to fourfront schema upgrade
* regenerated lock file 

2.1.1
=====

* fixes to GA publish script

2.1.0
=====

`PR:103 Various needed updates <https://github.com/4dn-dcic/dcicwrangling/pull/103>_`

* Update the version numbers for ChIP-seq pipeline update in functions/cleanup.py 
* Update Makefile to use newer version of poetry and publish with new dcicutils script
* add tag-and-push script to commands
* update the github action publish 
* Update pyproject.toml to use new dcicutils version
* Relock the dependencies in poetry.lock

2.0.1
=====

* Update to ubuntu version 20.04 for running github workflows

2.0.0
=====

* Update the version of dcicutils used to go along with es upgrade
* Tweak to GEO dbxref notebook to prevent accidentally adding the same accession more than once

1.3.0
=====

* Add new useful notebook to help in adding GEO/SRA dbxrefs to items

1.2.4
=====

* Bug fix in notebook 04: expsets were not unique in publication.


1.2.3
=====

* Bug fix in notebook 04: ``exp_sheet`` was missing.
* Up to 5 channels are supported now.


1.2.2
=====

* Small improvements in the notebook to replace uploaded files, adding
  extra_files and improving the search query and variable names.
* Bug fix: some "empty" cells were not handled correctly.


1.2.1
=====

* Fix a bug in status level for UserContent items.


1.2.0
=====

* Added new notebook to replace uploaded files and delete linked items.


1.1.0
=====

`PR 90: Geo2fdn update <https://github.com/4dn-dcic/dcicwrangling/pull/90>`_

* Uses openpyxl in geo2fdn script - now this script handles ``xlsx`` files.
  This is compatible with files produced by Submit4dn v2.2.0 and up.
  ``xls`` files are not supported anymore.
* Remove xlrd, xlwt, xlutils dependencies in the entire repo, as this script was
  the only remaining one to be upgraded to use openpyxl.
  This could be a breaking change in case of untracked scripts/notebooks.
* Bug fix in geo2fdn script: FileFastq tab is now written properly.


1.0.0
=====

`PR 89: update dependencies <https://github.com/4dn-dcic/dcicwrangling/pull/89>`_

* update some dependencies including using dcicutils 4.1 and up - this causes some breaking changes and it is likely that some notebooks may stop working - especially copies in untracked folders
* updated script utils functions for validation and the scripts that use them to allow specification of key and keyfile as strings rather than previously used key dict passed to key argument
* fixed tests to use new function


0.5.6
=====

`PR 88: remove deleted items from store <https://github.com/4dn-dcic/dcicwrangling/pull/88>`_

* Bug fix: items patched by delete_wfrs() are now removed from store, to prevent un-deleting.
* Bug fix: protected data check is needed only when individual is human.

0.5.5
=====

`PR 85: Update scripts <https://github.com/4dn-dcic/dcicwrangling/pull/85>`_

* Add an optional arg to `omit_note` in generate_wfr_from_pf.
* Change attribution of File Provenance Tracking WorkFlowRun to match the one of the output file.

0.5.4
=====

* Add this CHANGELOG and test warning if it's not updated

0.5.3
=====

0.2.0
=====

0.1.7
=====

0.1.3
=====
