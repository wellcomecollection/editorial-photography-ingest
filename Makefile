.PHONY: shoots/clean %.sliced
.SECONDARY:

# Remove intermediate/final files from the shoots folder
shoots/clean:
	rm shoots/*restored
	rm shoots/*transferred
	rm shoots/*slice*

# Request the Glacier restoration of the shoots in the given file
# The file is expected to contain one shoot identifier per line.
%.restored : %
	cat $< | AWS_PROFILE=workflow-developer python src/restore.py
	cp $< $@


# Request the Glacier transfer of the shoots in the given file
# This rule depends on restoration having completed, which is not guaranteed
# (or even likely) if you run this rule without having previously requested the restoration
# Any shoots that are not yet fully restored will result in a DLQ message that can eventually
# be redriven when the s3 objects are finally available for download

# transfer to staging (see above)
%.transferred.staging: %.restored
	cat $< | AWS_PROFILE=digitisation-developer python src/start_transfers.py staging
	cp $< $@


# transfer to production (see above)
%.transferred.production: %.restored
	cat $< | AWS_PROFILE=digitisation-developer python src/start_transfers.py production
	cp $< $@

# Slice a given input file into manageable chunks, so that you can run them through the
# transfer process separately without overwhelming the target system.
# The right number for archivematica is probably about 20.

%.sliced: %
	split -l 20 $< $<.

%.touched.staging: %
	cat % | AWS_PROFILE=digitisation-developer python src/touch.py staging

%.touched.production: %
	cat % | AWS_PROFILE=digitisation-developer python src/touch.py production
