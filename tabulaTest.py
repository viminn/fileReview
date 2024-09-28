import tabula

tables = tabula.read_pdf("SSR.pdf", pages="all")
# print(tables)
df = tables[0]
print(df)