#
# Example python script to generate a BOM from a KiCad generic netlist
#
# Example: Sorted and Grouped CSV BOM
#

"""
    @package
    Output: CSV (comma-separated)
    Grouped By: Value, Footprint
    Sorted By: Ref
    Fields: Ref, Qnty, Value, Cmp name, Footprint, Description, Vendor

    Command line:
    python "pathToFile/bom_csv_grouped_by_value_with_fp.py" "%I" "%O.csv"
"""

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
import kicad_utils
import csv
import sys

# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    f = kicad_utils.open_file_writeUTF8(sys.argv[2], 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout

# Create a new csv writer object to use as the output formatter
out = csv.writer(f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

# Output a set of rows for a header providing general information
out.writerow(['Source:', net.getSource()])
out.writerow(['Date:', net.getDate()])
out.writerow(['Tool:', net.getTool()])
out.writerow( ['Generator:', sys.argv[0]] )
out.writerow(['Component Count:', len(net.components)])
out.writerow(['Ref', 'Qnty', 'Value', 'Cmp name', 'Footprint', 'Description', 'RS order number'])


# Get all of the components in groups of matching parts + values
# (see ky_generic_netlist_reader.py)
groupedComponents = net.groupComponents()

class Component():
    def __init__(self, reference, value, partName, footprint, description, orderNumber):
        self.reference = reference
        self.value = value
        self.partName = partName
        self.footprint = footprint
        self.description = description
        self.orderNumber = orderNumber

    def __str__(self):
        return f"{self.reference}: {self.value}, {self.orderNumber}"


components = []

for group in groupedComponents:
    for component in group:
        convertedComponent = Component(
            reference=component.getRef(),
            value=component.getValue(),
            partName=component.getPartName(),
            footprint=component.getFootprint(),
            description=component.getDescription(),
            orderNumber=component.getField("RS order number"))
        components.append(convertedComponent)
        
componentsByOrderNumber = {}

for component in components:
    if component.orderNumber in componentsByOrderNumber:
        componentsByOrderNumber[component.orderNumber].append(component)
    else:
        componentsByOrderNumber[component.orderNumber] = [component]


for componentsList in componentsByOrderNumber.values():
    seperator = ", "
    references = seperator.join([component.reference for component in componentsList])
    values = seperator.join([component.value for component in componentsList])
    component = componentsList[0]

    out.writerow([
        references,
        len(componentsList),
        values,
        component.partName,
        component.footprint,
        component.description,
        component.orderNumber])