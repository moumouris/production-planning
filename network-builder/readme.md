To build a network and then optimize it using an excel file:

1.Add an excel file in the root of this folder in the same format like example.xlsx where:
  First column stands for materials, enter raw, intermediate and final materials in this order
  First row is for units 
  Second row is for tasks
  Tasks below a unit belong in this unit
  1 stands for material is produced by task
  -1 stands for material is consumed by task

2. Run network-builder.py file, it will construct a folder with excel files to be filled with other required data for
our model

3. After you've filled the newly created excel files with the required data Run runModels.py to optimize your network