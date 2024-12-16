def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    # Lista de números para sumar
    numbers = [1, 2, 3, 4, 5]
    
    # Punto de interrupción potencial aquí
    result = calculate_sum(numbers)
    
    print(f"La suma de los números {numbers} es: {result}")

if __name__ == "__main__":
    main()
