

default:
	@type Makefile


1:
	quarto render scanner.qmd

all:
	quarto render scanner.qmd --to markdown
	copy scanner.md .\qmds\scanner.md
	cd ./qmds & quarto render & cd ..
