if __name__ == '__main__':
    n = int(input())
    student_marks = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()
    sum=0
    for i in student_marks: 
        if i==query_name: 
            for j in student_marks[i]: 
                sum+=j 
                avg=sum/len(student_marks[i]) 
    print('%.2f'%avg)
