# 함수 정의
def add(x, y): return x + y
def subtract(x, y): return x - y
def multiply(x, y): return x * y
def divide(x, y): return x / y if y != 0 else "Error"

# 사용자 입력
num1 = float(input("첫 번째 숫자: "))
operator = input("연산자 (+, -, *, /): ")
num2 = float(input("두 번째 숫자: "))

# 계산 및 출력
if operator == '+': print(add(num1, num2))
elif operator == '-': print(subtract(num1, num2))
elif operator == '*': print(multiply(num1, num2))
elif operator == '/': print(divide(num1, num2))
else: print("잘못된 연산자")
#ㅇㅇㄹㅇㄹㄴㄹffffff