import frappe

def get_total_uom(items):
    branches = ['cty', 'jrb', 'mll', 'osm', 'mlby', 'val', 'crm', 'btu', 'ilgmain', 'ilgmall', 'bml', 'suki', 'cmgn',
                'pml', 'tbd', 'vmt', 'val2']
    total_qty_per_branch = dict.fromkeys(branches, 0)
    data = {}
    uom = []
    
    for item in items:
        # Loop through all items and insert uoms used in document
        uom.append(item.uom)

        # Loop over all branches and insert total qty per branch
        for branch in total_qty_per_branch:
            total_qty_per_branch[branch] += item.get(branch)

    # Inititalize uom list
    uom = list(set(uom))

    # Initialize data with all branches adn total_uom
    # Condition: only initialize branches with qty < 0
    data = {x: {'uom': dict.fromkeys(uom, 0)} for x,y in total_qty_per_branch.items() if y != 0 }
    data['total_uom'] = dict.fromkeys(uom, 0)

    for item in items:
        # Loop over all branches
        for branch in data:
            if branch != 'total_uom':
                # then increment item qty per branch
                data[branch]['uom'][item.uom] += item.get(branch)
                data['total_uom'][item.uom] += item.get(branch)

    print(data)
    print(total_qty_per_branch)
    return data