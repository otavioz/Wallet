"""
List os classes based on Google Sheet structured data.
"""

class EntradaModel:
    table = f'Entrada!B3:H99'
    card = 0
    check = 1
    id_ = 2
    name = 3
    serie = 4
    repetition = 5
    weight = 6
    

class HistoryModel:
    table = f'Histórico!A2:F'
    date = 0
    card = 1
    id_ = 2
    serie = 3
    repetition = 4
    weight = 5

class ExerciseModel:
    table = f'Exercícios!A2:C'
    name = 0
    id = 1
    description = 2