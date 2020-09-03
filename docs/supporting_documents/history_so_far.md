## Brain dump notes of the history of Casrec

- About 10 years ago, PGO was split up into Public guardian and court of protection but both kept using casrec.
As such users often have access to data they shouldn't have. All OPG data needs to be in Sirius.
- Supervision Data is when court have appointed someone to be a deputy and all the data about them is stored in Casrec.
- The CasRec database is CyberScience cyberquery which is basically a flat file database brought together by abstraction layer.
- The Register is a statutory requirement for everyone who has a deputyship and all clients who are incapacitated to run their lives.
- Access to Casrec only available on dom1 and Infrastructure is managaed by ATOS.
- Meris stored docs and data. Casrec only stores data. Live link (running out of space) stores docs that are linked to from casrec.
- Sirius got a load of docs off livelink and had some stub records created against them.
- We need to make sure the stub case gets populated and not just new cases.
- 'Methods' managed service came in to manage the migration but they were not up to the task, though they have provided us initial mapping documents.
- Sirius has no data structs for PA and Pro deputies currently
- We need to implement an entity based approach
