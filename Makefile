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
# The number here is based on the original input file containing 907 shoots,
# so this creates 9 files of about 100.
# The right number is yet to be discovered.
# The right number is yet to be discovered.
%.sliced: %
	split -l 101 $< $<.

# Touch the sho
%.touched: %
	cat % | xargs aws s3 cp \
    --metadata 'touched=touched' \
    --recursive --exclude="*" \
    --include="$2" \
    "${@:3}" \
    "$1" "$1"
