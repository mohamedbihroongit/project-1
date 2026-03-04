import random

def create_seating_arrangement(student_list, rows, cols):
    shuffled_students = list(student_list)
    random.shuffle(shuffled_students)
    
    arrangement = []
    student_index = 0
    total_capacity = rows * cols
    
    if len(shuffled_students) > total_capacity:
        return None, f"Error: Hall capacity ({total_capacity}) is less than student count ({len(shuffled_students)})!"

    for r in range(1, rows + 1):
        row_data = []
        for c in range(1, cols + 1):
            if student_index < len(shuffled_students):
                row_data.append(shuffled_students[student_index])
                student_index += 1
            else:
                row_data.append("-") # Empty seat
        arrangement.append(row_data)
                
    return arrangement, None
