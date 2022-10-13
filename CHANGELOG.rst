===============
dcicwrangling
===============

----------
Change Log
----------

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
