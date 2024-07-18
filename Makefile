
%.restored.txt : %.txt
	cat $< | AWS_PROFILE=workflow-developer python src/restore.py
	cp $< $@

%.transferred.txt: %.restored.txt
	cat $< | AWS_PROFILE=digitisation-developer python src/start_transfers.py
	cp $< $@
