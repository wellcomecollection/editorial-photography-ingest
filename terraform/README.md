# Restore and Transfer pipeline
## How does it all fit together?

In the evening, the Restorer 
* Pulls a day's worth of shoots from the restore
* Restores the from Glacier
* Notifies the transfer throttle queue.

Restoration takes a nondeterministic amount of time up to 12 hours
```mermaid
sequenceDiagram
    Restore Schedule->>+Restorer: It's 2000
    Restorer->>+Restore Queue: Gimme 60
    Restore Queue -->> Restorer: OK
    Restorer->>S3:Restore
    S3 -->>Restorer: On it!
    Restorer->>-Transfer Throttle Queue:60 shoots
```

Across the day, the transfer throttle 
* pulls a manageable quantity from its queue
* shifts them onto the transfer queue

The transferrer then transfers everything on its queue
```mermaid
sequenceDiagram
    Transfer Schedule->>+Transfer Throttle: It's time
    Transfer Throttle ->> Transfer Throttle Queue: Gimme 10
    Transfer Throttle Queue-->> Transfer Throttle: OK
    Transfer Throttle->>- Transfer Queue: 10 shoots
    Transfer Queue ->>+ Transferrer:  10 shoots
    Transferrer->> Photography S3: Gimme Shoots
    PhotographyS3 -->> Transferrer: OK
    Transferrer ->>- Archive S3: 10 Shoots
```
