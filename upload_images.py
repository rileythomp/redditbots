if __name__ == '__main__':
    import csv
    from db import NbaDB
    db = NbaDB()
    f = open('images.csv')
    rows = csv.reader(f)
    i = 0
    for row in rows:
        i += 1
        if i > 614:
            db.add_image(row[0], f'https://nbapics.s3.amazonaws.com/{"-".join(row[0].split())}.svg')
        elif row[1] != '':
            db.add_image(row[0], f'https://nbapics.s3.amazonaws.com/{"-".join(row[0].split())}.png')
        else:
            db.add_image(row[0], row[1])
    db.close()