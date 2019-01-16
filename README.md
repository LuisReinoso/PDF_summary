# PDF_Summary 
> Obtén el resumen de un pdf en una sola página.

## Dependencias
- pdfminer.six
- sumy
- PyPDF2
- NLTK tokenizers punkt

## Instalación
- clonar repositorio
	``` bash
	git clone https://github.com/LuisReinoso/PDF_summary
	cd PDF_summary
	```
- instalar dependencias
	``` bash
	pip3 install -r ./requirements.txt
	```

## Uso
- ejecutar main.py
	``` bash
	python3 main.py
	```
- insertar la ruta del pdf a resumir
	``` bash
	./ejemplo.pdf
	```
- insertar la ruta de salida para el resumen
	``` bash
	./resumen/
	```
- seleccionar el algoritmo para crear el resumen. Cada algoritmo trabaja de forma diferente, produce resultados diferentes
	```
	press 1 and enter for Luhn.
	press 2 and enter for Lsa.
	press 3 and enter for LexRank.
	press 4 and enter for TextRank.
	press 5 and enter for SumBasic.
	press 6 and enter for KLsum.
	press 0 and enter to exit.
	```
- una vez completado el resumen este estará en la dentro de `./resumen/Summary/`. El nombre del archivo tiene como prefijo el nombre del algoritmo seleccionado y el time stamp como subfijo.
	``` bash
	./resumen/Summary/*.txt
	```

## Nota
- El pdf no debe ser un conjunto de imagenes ya que este proyecto no aplica OCR para reconocer caracteres.
- El pdf debe tener tabla de contenido o bookmarks

## Fork
Este proyecto es un fork de https://github.com/AmitabhSB/PDF_summary

## Licencia
Ver archivo [Licence](LICENSE)