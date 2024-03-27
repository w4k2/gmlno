tables:
	python 99_results.py
	pdflatex tables_/article.tex
	rm article.aux article.log article.out

graph_tables:
	python 100_graph_results.py
	pdflatex tables_/article_g.tex
	rm article_g.aux article_g.log article_g.out

new_table:
	python 98_results2.py
	pdflatex tables_/article.tex
	rm article.aux article.log article.out