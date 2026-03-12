# - Felipe Augusto Baleche Goncalves - FelipeABG
# - Giuseppe Bruno Ferreira Filippin - giuseppefilippin
# - Isabelle Lopes Kulczynskyj - isaabellelopes
# - Pedro Bastos Leite - PedroLeite3005

# Grupo: RA1 10

import sys 

def main():
    try:
        file_path = sys.argv[1]
        file_content = open(file_path, "r").readlines()
    except IndexError:
        print(f"Usage: {sys.argv[0]} [path-to-file]")
    except FileNotFoundError:
        print("Error: the provided file could not be opened or does not exist")

if __name__ == "__main__":
    main()
