@echo off
cd /d "C:\Users\repuestos01\Documents\Programas\data_scraper_sistema"
"C:\Users\repuestos01\AppData\Local\Programs\Python\Python313\Scripts\uv.exe" run main.py --dep-inicio "9" --dep-final "9" --cod-desde "120.1" --cod-hasta "125.1" --fecha-desde "01/01/2025"

run main.py --opcion "EXISTENCIA_STOCK" --dep-inicio "9" --dep-final "9" --cod-desde "1.1" --cod-hasta "999.99999" --salida "\\sistema01\SANANTONIO\NUDO\Nico Foley\existencias"