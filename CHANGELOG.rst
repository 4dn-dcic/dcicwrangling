===============
dcicwrangling
===============

----------
Change Log
----------

1.0.0
=====

`PR 89: update dependencies <https://github.com/4dn-dcic/dcicwrangling/pull/89>`

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
