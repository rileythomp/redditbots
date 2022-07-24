if __name__ == '__main__':
    import csv
    from db import NbaDB
    db = NbaDB
    f = open('images.csv')
    rows = csv.reader(f)
    for row in rows:
        print(f'adding {row[0]} {row[1]}')
        db.add_image(row[0], row[1])
        print(f'added {row[0]} {row[1]}')
    db.close()

