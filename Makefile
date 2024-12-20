.PHONY: shoots/clean %.sliced shoots/%.failed
.SECONDARY:

# Remove intermediate/final files from the shoots folder
shoots/clean:
	rm shoots/*restored
	rm shoots/*transferred
	rm shoots/*slice*
	rm shoots/*failed*
	rm shoots/*transfer_status

# Slice a given input file into manageable chunks, so that you can run them through the
# transfer process separately without overwhelming the target system.
# The right number for archivematica is probably about 20.

%.sliced: %
	split -l 20 $< $<.

# Request the Glacier restoration of the shoots in the given file
# The file is expected to contain one shoot identifier per line.
# In order to run this, set your AWS profile to one with authority in the platform account.
%.restored : %
	cat $< | python src/restore.py
	cp $< $@


# Request the Glacier transfer of the shoots in the given file
# This rule depends on restoration having completed, which is not guaranteed
# (or even likely) if you run this rule without having previously requested the restoration
# Any shoots that are not yet fully restored will result in a DLQ message that can eventually
# be redriven when the s3 objects are finally available for download
# In order to run this, set your AWS profile to one with authority in the digitisation account.

# transfer to staging (see above)
%.transferred.staging: %.restored
	cat $< | python src/start_transfers.py staging
	cp $< $@


# transfer to production (see above)
%.transferred.production: %.restored
	cat $< | python src/start_transfers.py production
	cp $< $@

# Touch the files already in Archivematica source bucket. This will stimulate the corresponding transfer lambdas.
# The target system can sometimes be unexpectedly unavailable or overwhelmed,
# resulting in failures.
# This allows us to invoke the process from just before the failure
# In order to run this, set your AWS profile to one with authority in the digitisation account.
%.touched.staging: %
	cat $< | python src/touch.py staging

%.touched.production: %
	cat $< | python src/touch.py production

# The target system has a habit of failing for ephemeral reasons.
# Failures are logged, so a list can be generated from the logs
# which can then be provided to .touched. above.
# compile a list of shoots that failed since a given time, thus:
# make shoots/2024-08-06T15:33:00Z.failed
shoots/%.failed: src/compile_failure_list.py
	python client/compile_failure_list.py $* > $@

# Once the whole thing is done, check that everything has actually gone through
# This produces a CSV recording
# True (successfully transferred) or False (not successfully transferred)
# against each shoot
%.transfer_status: %
	cat $< | AWS_PROFILE=${SOURCE_PROFILE} python client/compile_pending_list.py $* > $@

# Compile lists for retrying:

# Some things may have failed in the target system
# These are s3 keys that can be passed through the 'touched' target
%.touchable: %
	grep False $< | sed 's/,.*//' | AWS_PROFILE=${TARGET_PROFILE} python client/touchable.py production > $@

# Others may have failed to transfer (or have been deleted from the target bucket due to expiry)
# These are shoot identifiers that need to go back through the whole system again
%.needs_transfer: %
	grep False $< | sed 's/,.*//' | AWS_PROFILE=${TARGET_PROFILE} python client/untouchable.py production | sed 's/.*2754_//' | sed 's/\.zip//' > $@

%.queued_for_touch.production: %.transfer_status.touchable
	cat $< | AWS_PROFILE=${TARGET_PROFILE} python client/queue_touches.py production

%.queued_for_transfer.production: %.transfer_status.needs_transfer
	cat $< | AWS_PROFILE=${SOURCE_PROFILE} python client/start_restores.py production
