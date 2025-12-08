import random


def generate_graph(n:int , m: int, output:str):

    with open(f"{output}.txt", 'w', encoding='UTF-8') as fd:
        for u in range(n):
            for v in range(n, n + m):
                if random.random() < 0.3:
                    fd.write(f"{u} {v}\n")

def main():
    n = int(input("Enter number of nodes (n): "))
    m = int(input("Enter number of edges (m): "))
    output = input("Enter output file name: ")
    generate_graph(n, m, output)
    print("done")

if __name__ == "__main__":
    main()