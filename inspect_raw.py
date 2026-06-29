import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='skripsi_cctv', charset='utf8mb4')
cursor = conn.cursor()

# Cek variasi format harga
print('=== Sample Harga (COL 4) ===')
cursor.execute("SELECT DISTINCT `COL 4` FROM produk WHERE `COL 4` != 'Harga' LIMIT 10")
for r in cursor.fetchall():
    print(' ', repr(r[0]))

# Cek variasi format popularitas
print('\n=== Sample Popularitas (COL 7) ===')
cursor.execute("SELECT DISTINCT `COL 7` FROM produk WHERE `COL 7` NOT IN ('Popularitas', '') LIMIT 15")
for r in cursor.fetchall():
    print(' ', repr(r[0]))

# Cek variasi rating
print('\n=== Sample Rating (COL 6) ===')
cursor.execute("SELECT DISTINCT `COL 6` FROM produk WHERE `COL 6` NOT IN ('Rating', '') LIMIT 10")
for r in cursor.fetchall():
    print(' ', repr(r[0]))

# Cek data null/kosong
print('\n=== NULL/Empty check ===')
cursor.execute("SELECT COUNT(*) FROM produk WHERE `COL 4` = '' OR `COL 4` IS NULL")
print('Harga kosong:', cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM produk WHERE `COL 6` = '' OR `COL 6` IS NULL")
print('Rating kosong:', cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM produk WHERE `COL 7` = '' OR `COL 7` IS NULL")
print('Popularitas kosong:', cursor.fetchone()[0])

# Cek nama produk contoh untuk brand extraction
print('\n=== Sample Nama Produk (COL 3) ===')
cursor.execute("SELECT `COL 3` FROM produk WHERE `COL 3` != 'Nama' LIMIT 10")
for r in cursor.fetchall():
    print(' ', repr(r[0]))

conn.close()
