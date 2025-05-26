# BulkCatAssignment

## Purpose
Assign categories to VM fron a csv file.

## Usage

### Prerequisites
- create a python virtual enc, avtivate it then run `pip install -r requirements.txt`
- prepare csv file :
  - 1st line are headers
  - 1st column must have VM name
  - 6th columm must have 1st category assignment (can be change with variable `categoryStartColumn` in the script)

Note : Columm header will be used as the cat key, case value will represent the category value.

### Usage
- `python.py <CSV file>` 

## Current limitations 
- The scripte does not check assignment result, it just initialize the assigment
- It does not create categories, they have to be created before launching it
- It does not handle category update. If the VM already has category assigned with the same key (and different value), assignment will fail