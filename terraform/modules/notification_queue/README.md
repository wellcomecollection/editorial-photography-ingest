# Notification Queue

This module creates a queue/topic pair. Notifications sent to the topic
will become messages on the queue.

If the queue needs to also subscribe to other topics, then these can be 
provided as extra_topics.