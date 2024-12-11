import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# Початковий датасет
X_train = np.array([[1, 2], [2, 3], [3, 1]])
y_train = np.array([0, 1, 0])

# Нові дані, які додаються поступово
new_data = [
    (np.array([[4, 5], [5, 4]]), np.array([1, 1])),
    (np.array([[6, 7], [7, 6]]), np.array([1, 1])),
    (np.array([[0, 1], [1, 0]]), np.array([0, 0]))
]

# Ініціалізація моделі
model = LogisticRegression()

# Список для відстеження точності
accuracies = []

# Цикл оновлення моделі
for i, (X_new, y_new) in enumerate(new_data):
    # Об'єднання нового датасету зі старим
    X_train = np.vstack((X_train, X_new))
    y_train = np.hstack((y_train, y_new))

    # Тренування моделі на оновленому датасеті
    model.fit(X_train, y_train)

    # Передбачення і обчислення точності
    y_pred = model.predict(X_train)
    acc = accuracy_score(y_train, y_pred)
    accuracies.append(acc)

    print(f"Ітерація {i + 1}: Точність = {acc:.2f}")

# Візуалізація покращення моделі
plt.plot(range(1, len(accuracies) + 1), accuracies, marker='o')
plt.title('Покращення точності моделі з кожною ітерацією')
plt.xlabel('Ітерація')
plt.ylabel('Точність')
plt.grid(True)
plt.show()
