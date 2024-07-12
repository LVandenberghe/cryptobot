##
## EPITECH PROJECT, 2024
## trade [WSL: Ubuntu]
## File description:
## Makefile
##

all: trade

trade: trade.py
	@echo '#!/usr/bin/env python3' | cat - trade.py > trade
	@chmod +x trade

clean:

fclean: clean
	@rm -f trade

re: fclean all

.phony: all clean fclean re
