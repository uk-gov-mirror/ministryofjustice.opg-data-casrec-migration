---
layout: page
title:  "Mapping Document"
date:   2020-10-29 14:51:23 +0000
categories: mapping
resouce: true
---

Mapping Document
==================


Spreadsheet format
------------------

|          | Column Name             | Populated By | Details                         |
| -------- | ----------------------- | ------------ | ------------------------------- |
| Sirius   | column_name             | Sirius db    | Do not amend                    |
| Sirius   | data_type               | Sirius db    | Do not amend                    |
| Sirius   | is_pk                   | Sirius db    | Do not amend                    |
| Sirius   | fk_children             | Sirius db    | Do not amend                    |
| Sirius   | fk_parents              | Sirius db    | Do not amend                    |
| Casrec   | casrec_table            |              | Must match table name exactly   |
| Casrec   | casrec_column_name      |              | Must match column name exactly* |
| Analysis | requires_transformation |              | Choose from list (see below)    |
| Analysis | default_value           |              | If required                     |
| Analysis | is_complete             |              | Yes or No                       |
| Analysis | comments                |              |                                 |



### <u>Sirius Columns</u>

​	The first 5 rows will be generated directly from the Sirius database, please do not amend these.

### <u>Casrec Columns</u>

​	These will need to match the Casrec table and column names exactly. Case insensitve.

#### casrec_column_name - multiple columns

​	In the case that one column in Sirius is mapped to multiple columns in Casrec, then please do NOT duplicate the Sirius row, instead enter the `casrec_column_name` as a comma separated list, eg `Item1, Item2, Item3`

### <u>Analysis Columns</u>

​	These are to be filled in by the Migrations team.

#### requires_transformation

​	To be chosen from a list of standard transformations, current list is:

* `squash_columns`  converts a comma seperated list of columns into a single json array

* `convert_to_bool` casrec data is all stored as strings, this makes it into a proper boolean

* `unique_number` generates a unique 12 digit number

  These are just the basics at the moment, more will be added as we need them.

#### default_value

​	If the column has a default value, this is the place to put it. Currently this is only applied when a casrec column is not mapped, so can't be used as a kind of backup of the casrec data is null. 

#### is_complete

​	If we are totally happy with this mapping, set this to `Yes`. It will help keep track of what our unknowns are.

#### comments

​	For only your most insightful and interesting comments

#### etc etc etc...

​	Feel free to add more columns, but they will be for human reference only, and will not be used by the transformations.