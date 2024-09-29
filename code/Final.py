import csv
import os
import random
from prettytable import PrettyTable

#Chunking
def splitcsv(ipfile, opfolder, maxmem):
    chunksize = 5000
    header = None
    current = 1

    with open(ipfile, 'r', encoding='utf-8-sig') as f:
        while True:
            data = []
            currentmem = 0

            if header is None:
                header = f.readline().strip().split(',')
                data.append(header)

            while currentmem < maxmem and len(data) < chunksize:
                line = f.readline()
                if not line:
                    break

                linemem = sum(len(col) for col in line.strip().split(',')) / (1024 * 1024)
                if (currentmem + linemem) > maxmem:
                    break

                data.append(line.strip())
                currentmem += linemem

            if not data:
                break

            opfile = f'{opfolder}/RFSignalData_{current}.csv'
            with open(opfile, 'w', newline='', encoding='utf-8') as output:
                csvwriter = csv.writer(output)
                csvwriter.writerow(header)
                for row in data[1:]:
                    csvwriter.writerow(row.split(','))

            current += 1

opfolder = '/Users/khushigandhi/Desktop/Chunks'
os.makedirs(opfolder, exist_ok=True)

splitcsv('/Users/khushigandhi/Desktop/RFSignalData.csv', opfolder, maxmem=100)

#Table Creation
def createtable(chunkfolder, query):
    chunkfiles = [f for f in os.listdir(chunkfolder) if f.startswith('RFSignalData_') and f.endswith('.csv')]

    if not chunkfiles:
        raise ValueError("No chunk files found in the specified folder.")

    selectedfile = random.choice(chunkfiles)
    selectedpath = chunkfolder + '/' + selectedfile

    with open(selectedpath, 'r', encoding='utf-8-sig') as f:
        qpart = query.split("with columns:")
        if len(qpart) != 2:
            raise ValueError("Invalid query format. Please use 'produce table <table> with columns: <column> <dtype>'.")

        seperator = qpart[0].split("table")
        if len(seperator) != 2:
            raise ValueError("Invalid query format. Please use 'produce table <table> with columns: <column> <dtype>'.")
        produce, tablename = (part.strip() for part in seperator)

        colstype = qpart[1]
        types = [c.strip().split() for c in colstype.split(',')]

        header = next(f).strip().split(',')
        for col, _ in types:
            if col not in header:
                raise ValueError(f"Column '{col}' not found in the selected chunk file.")

        table = PrettyTable([col for col, _ in types])
        table.align = 'l'  

        for line in f:
            data = line.strip().split(',')
            table.add_row([data[header.index(col)] for col, _ in types])

        print(f"\n{table}\n")

        tablesfolder = '/Users/khushigandhi/Desktop/Tables'
        os.makedirs(tablesfolder, exist_ok=True)
        csvfn = os.path.join(tablesfolder, f"{tablename}.csv")
        print(f"tablename: {tablename}")
        with open(csvfn, 'w', newline='', encoding='utf-8') as csv_file:
            header_line = ''
            for col, _ in types:
                header_line += col + ','
            csv_file.write(header_line.rstrip(',') + '\n')

            f.seek(0)  
            next(f)  
            for line in f:
                data = [line.strip().split(',')[header.index(col)] for col, _ in types]
                dataline = ','.join(data)
                csv_file.write(dataline + '\n')

        print(f"Data saved as '{csvfn}'.\n")

        return f"{produce} {tablename} with columns: {colstype}", tablename

#Projection
def display(table_folder, query):
    qparts = query.split("from")
    if len(qparts) != 2:
        raise ValueError("Invalid query format. Please use 'display <column(s)> from <table>'.")

    disppart = qparts[0].strip()
    columns = [col.strip() for col in disppart.split("display")[-1].split(",")]

    table_name = qparts[1].strip()

    tablepath = os.path.join(table_folder, f"{table_name}.csv")
    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{table_name}' not found.")

    with open(tablepath, 'r', encoding='utf-8-sig') as table_file:
        t_reader = csv.reader(table_file)
        header = next(t_reader)

        if "all" in columns:
            columns = header 

        for col in columns:
            if col not in header:
                raise ValueError(f"Column '{col}' not found in the table '{table_name}'.")

        col_indices = [header.index(col) for col in columns]

        disptable = PrettyTable(columns)
        for row in t_reader:
            disptable.add_row([row[idx] for idx in col_indices])

        print(f"\n{disptable}\n")

#Filtering
def filters(tablesfolder, query):
    parts = query.split()

    fidx = parts.index('from')
    widx = parts.index('where')

    tablename = parts[fidx + 1]
    conditions = ''
    for i in range(widx + 1, len(parts)):
        conditions += parts[i] + ' '
    conditions = conditions.strip()
    
    tablepath = os.path.join(tablesfolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    filtered_data = []

    with open(tablepath, 'r', newline='', encoding='utf-8') as table_file:
        treader = csv.reader(table_file)
        table_header = next(treader)

        for row in treader:
            if checks(row, table_header, conditions):
                filtered_data.append(row)

    restable = PrettyTable(table_header)
    restable.align = 'l'

    for row in filtered_data:
        restable.add_row(row)

    print(f"Filtered Result from '{tablename}':")
    print(restable)

def checks(row, header, conditions):
    try:
        for col in header:
            col_index = header.index(col)
            value = row[col_index]

            if value.replace('.', '', 1).isdigit():
                conditions = conditions.replace(col, f"{float(value)}")
            else:
                conditions = conditions.replace(col, f'"{value}"')

        return eval(conditions)
    except Exception as e:
        print(f"Error evaluating conditions: {e}")
        return False

#Insertion
def insert(tablefolder, query):
    parts = query.split()

    eidx = parts.index('include')
    inidx = parts.index('in')
    widx = parts.index('with')

    entry = parts[eidx + 6:inidx] 
    values = parts[widx + 1:]

    vals = ' '.join(values)

    evsep = [part.strip() for part in vals.split(',')]

    tablename = parts[inidx + 1]

    tablepath = os.path.join(tablefolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    rows = []
    with open(tablepath, 'r', encoding='utf-8-sig') as tablefile:
        treader = csv.reader(tablefile)
        header = next(treader)
        for row in treader:
            rows.append(row)

    new_row = [None] * len(header)
    for evp in evsep:
        ent, value = [part.strip() for part in evp.split('==')]
        new_row[header.index(ent)] = value.strip()

    rows.append(new_row)

    with open(tablepath, 'w', newline='', encoding='utf-8') as tablefile:
        twriter = csv.writer(tablefile)
        twriter.writerow(header)
        twriter.writerows(rows)

    print(f"New entry included in '{tablename}': {new_row}")

#Updating
def edit(tablefolder, query):
    parts = query.split()

    eidx = parts.index('edit')
    tidx = parts.index('to')

    column = parts[eidx + 1]
    upval = parts[tidx + 1]
    condition = ' '.join(parts[tidx + 3:-2])  
    tablename = parts[-1]

    tablepath = os.path.join(tablefolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    uprows = []

    with open(tablepath, 'r', encoding='utf-8-sig') as tablefile:
        treader = csv.reader(tablefile)
        header = next(treader)

        if column not in header:
            raise ValueError(f"Column '{column}' not found in the table.")

        column_index = header.index(column)

        for row in treader:
            if eval(condition, dict(zip(header, row))):
                row[column_index] = upval
            uprows.append(row)

    with open(tablepath, 'w', newline='', encoding='utf-8') as tablefile:
        twriter = csv.writer(tablefile)
        twriter.writerow(header)
        twriter.writerows(uprows)

    print(f"Data in '{column}' column updated to '{upval}' where {condition} in '{tablename}'.")

#Deletion
def eliminate(tablefolder, query):
    parts = query.split()

    eidx = parts.index('eliminate')
    fidx = parts.index('from')
    widx = parts.index('where')

    tablename = parts[fidx + 1]
    conditions = ' '.join(parts[widx + 1:])

    tablepath = os.path.join(tablefolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    with open(tablepath, 'r', newline='', encoding='utf-8') as tablefile:
        treader = csv.reader(tablefile)
        header = next(treader)
        tabledata = list(treader)

    filtered_data = [row for row in tabledata if not eval(conditions, dict(zip(header, row)))]

    with open(tablepath, 'w', newline='', encoding='utf-8') as tablefile:
        twriter = csv.writer(tablefile)
        twriter.writerow(header)
        twriter.writerows(filtered_data)

    print(f"Entries eliminated from '{tablename}' where {conditions}.")

#Aggregation
def aggregate(tablesfolder, query):
    parts = query.split()

    fidx = parts.index('from')
    uidx = parts.index('using')

    columns = [col.strip(',') for col in parts[1:fidx]]  
    tablename = parts[fidx + 1]
    aggfn = parts[uidx + 1].lower() 

    aggfns = {
        'count': len,
        'sum': lambda x: sum(float(v) for v in x if isinstance(v, (int, float))),
        'min': lambda x: min(v for v in x if isinstance(v, (int, float))),
        'max': lambda x: max(v for v in x if isinstance(v, (int, float))),
        'avg': lambda x: sum(float(v) for v in x if isinstance(v, (int, float))) / len(x) if len(x) > 0 else 0,
    }

    if aggfn not in aggfns:
        print("Invalid aggregation function. Please use one of: count, sum, min, max, avg.")
        return

    tablepath = os.path.join(tablesfolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    column_data = {col: [] for col in columns}

    with open(tablepath, 'r', newline='', encoding='utf-8') as table_file:
        treader = csv.reader(table_file)
        table_header = next(treader)

        colidx = [table_header.index(col) for col in columns]

        for row in treader:
            for col, i in zip(columns, colidx):
                value = row[i]
                try:
                    value = float(value)
                except ValueError:
                    pass
                column_data[col].append(value)

    aggresult = {
        col: aggfns[aggfn](values) for col, values in column_data.items()
    }

    restable = PrettyTable(['Column', 'Aggregation Result'])
    restable.align = 'l'
    for col, result in aggresult.items():
        restable.add_row([col, result])

    print(f"Aggregated Result from '{tablename}':")
    print(restable)

#Ordering
def arrange(tablesfolder, query):
    parts = query.split()

    tidx = parts.index('in')
    cidx = parts.index('by')
    oidx = parts.index('with')

    tablename = parts[tidx + 1]
    column = parts[cidx + 1]
    order = parts[oidx + 1].lower()

    tablepath = os.path.join(tablesfolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    with open(tablepath, 'r', newline='', encoding='utf-8') as table_file:
        treader = csv.reader(table_file)
        header = next(treader)
        tabledata = list(treader)

    cidx = header.index(column)

    reverse_order = order == 'descending'
    tabledata.sort(key=lambda row: row[cidx], reverse=reverse_order)

    sortedtable = PrettyTable(header)
    sortedtable.align = 'l'  
    sortedtable.add_rows(tabledata)

    print(f"Arranged Data in '{tablename}' by '{column}' with '{order}' order:")
    print(sortedtable)
    
#Joining
def combines(tablesfolder, query):
    parts = query.split()
    if len(parts) != 8 or parts[0] != "combine" or parts[2] != "and" or parts[4] != "using" or parts[6] != "with":
        print("Invalid combine query format. Please use 'combine <table1> and <table2> using <column> with <join>'.")
        return

    table1 = parts[1]
    table2 = parts[3]
    common = parts[5]
    jointype = parts[7].lower()

    t1path = os.path.join(tablesfolder, f"{table1}.csv")
    t2path = os.path.join(tablesfolder, f"{table2}.csv")

    if not os.path.exists(t1path):
        raise FileNotFoundError(f"Table '{table1}' not found.")
    if not os.path.exists(t2path):
        raise FileNotFoundError(f"Table '{table2}' not found.")

    t1data = {}
    with open(t1path, 'r', newline='', encoding='utf-8') as table1_file:
        t1reader = csv.DictReader(table1_file)
        for row in t1reader:
            keyval = row[common]
            t1data[keyval] = row

    t2data = []
    with open(t2path, 'r', newline='', encoding='utf-8') as table2_file:
        t2reader = csv.DictReader(table2_file)
        for row in t2reader:
            t2data.append(row)

    resultdata = []
    if jointype == "inner":
        for row2 in t2data:
            keyval = row2[common]
            if keyval in t1data:
                combinedrow = {**t1data[keyval], **row2}
                resultdata.append(combinedrow)
    elif jointype == "left":
        for keyval, row1 in t1data.items():
            for row2 in t2data:
                if keyval == row2[common]:
                    combinedrow = {**row1, **row2}
                    resultdata.append(combinedrow)
                    break
            else:
                combinedrow = {**row1, **{col: None for col in t2data[0]}}
                resultdata.append(combinedrow)
    elif jointype == "right":
        for row2 in t2data:
            keyval = row2[common]
            if any(keyval == row1[common] for row1 in t1data.values()):
                combinedrow = {**next(row1 for row1 in t1data.values() if row1[common] == keyval), **row2}
                resultdata.append(combinedrow)
            else:
                combinedrow = {**{col: None for col in t1data.values().popitem()[1]}, **row2}
                resultdata.append(combinedrow)
    elif jointype == "cross":
        for row1 in t1data.values():
            for row2 in t2data:
                combinedrow = {**row1, **row2}
                resultdata.append(combinedrow)
    else:
        print("Invalid join type. Please use one of: inner, left, right, cross.")
        return

    if resultdata:
        resulttable = PrettyTable(resultdata[0].keys())
        resulttable.align = 'l'  

        for row in resultdata[:25]:
            resulttable.add_row(row.values())

        print(f"\nFirst 25 Rows of Combined Result of '{table1}' and '{table2}' using '{common}' with '{jointype}' join:")
        print(resulttable)
    else:
        print(f"No common key '{common}' found between '{table1}' and '{table2}' with '{jointype}' join.")

#Grouping      
def groupby(tablesfolder, query):
    parts = query.split()

    gidx = parts.index('group')
    fidx = parts.index('from')
    widx = parts.index('with')
    uidx = parts.index('using')

    grpcols = [col.strip(',') for col in parts[gidx + 1:fidx]]  
    tablename = parts[fidx + 1]
    display_columns = [parts[widx + 1]]
    aggfn = parts[uidx + 1].lower() 

    aggfns = {
        'count': len,
        'sum': lambda x: sum(float(v) for v in x if isinstance(v, (int, float))),
        'min': lambda x: min(v for v in x if isinstance(v, (int, float))),
        'max': lambda x: max(v for v in x if isinstance(v, (int, float))),
        'avg': lambda x: sum(float(v) for v in x if isinstance(v, (int, float))) / len(x) if len(x) > 0 else 0,
    }

    if aggfn not in aggfns:
        print("Invalid aggregation function. Please use one of: count, sum, min, max, avg.")
        return

    tablepath = os.path.join(tablesfolder, f"{tablename}.csv")

    if not os.path.exists(tablepath):
        raise FileNotFoundError(f"Table '{tablename}' not found.")

    column_data = {col: [] for col in display_columns}
    grpdata = {}

    with open(tablepath, 'r', newline='', encoding='utf-8') as table_file:
        treader = csv.reader(table_file)
        theader = next(treader)

        display_idx = theader.index(display_columns[0])

        for row in treader:
            grpkey = tuple(row[theader.index(group_col)] for group_col in grpcols)
            if grpkey not in grpdata:
                grpdata[grpkey] = []
            grpdata[grpkey].append(float(row[display_idx]))

    agg_result = {}
    for grpkey, group_values in grpdata.items():
        agg_result[grpkey] = aggfns[aggfn](group_values)

    restable = PrettyTable(grpcols + [f"{display_columns[0]} ({aggfn.capitalize()})"])
    restable.align = 'l'

    for grpkey, result in agg_result.items():
        result_row = list(grpkey) + [result]
        restable.add_row(result_row)

    print(f"Aggregated Result from '{tablename}':")
    print(restable)

def main():
    opfolder = '/Users/khushigandhi/Desktop/Chunks'
    os.makedirs(opfolder, exist_ok=True)

    chunkfolder = opfolder
    tablesfolder = '/Users/khushigandhi/Desktop/Tables'
    os.makedirs(tablesfolder, exist_ok=True)
    print("****************************************************************************************")
    print("\t\t\tWelcome to the Command Line Prompt")
    print("****************************************************************************************")
    while True:
        userip = input("Enter Query > ")
        if userip.lower() == 'exit':
            break
        elif userip.lower().startswith('splitcsv'):
            _, ipfile, opfolder, maxmem = userip.split()
            splitcsv(ipfile, opfolder, int(maxmem))
        elif userip.lower().startswith('produce table'):
            _, query = userip.split(maxsplit=1)
            createtable(chunkfolder, query)
        elif userip.lower().startswith('display'):
            _, query = userip.split(maxsplit=1)
            display(tablesfolder, query)
        elif userip.lower().startswith('edit'):
            edit(tablesfolder, userip)
        elif userip.lower().startswith('include a new entry in'):
            insert(tablesfolder, userip)
        elif userip.lower().startswith('compute'):
            aggregate(tablesfolder, userip)
        elif userip.lower().startswith('arrange the data in'):
            arrange(tablesfolder, userip)
        elif userip.lower().startswith('combine'):
            combines(tablesfolder, userip)
        elif userip.lower().startswith('eliminate'):
            eliminate(tablesfolder, userip)
        elif userip.lower().startswith('group'):
            groupby(tablesfolder, userip)
        elif userip.lower().startswith('give'):
            filters(tablesfolder, userip)
        else:
            print("Invalid query.")

if __name__ == "__main__":
    main()