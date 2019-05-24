def print_slide(state):
    for row in state:
        print(row)

state0 = [[ 0 for i in range(10)] for j in range(10)]
state1 = [[ 2 for i in range(10)] for j in range(10)]

curState = state0[:]

print("state start")
print_slide(state0)
print("state end")
print_slide(state1)

print("right to left")

for i in range(len(state0)):
    for j in range(len(state0[0])):
        pass
    curState[i] = state1[i]

    print("curState, step", i)
    print_slide(curState)


curState = state0[:]
print("Left to right")

for j in range(len(state0)):
    for i in range(len(state0[0])):
        curState[i][j] = state1[i][j]

    print("curState, step", j)
    print_slide(curState)

curState = [[ 0 for i in range(10)] for j in range(10)]
print("Left top conner to right")
for row in range(len(state0)):
    for row2 in range(row+1):
        for col in range(row+1):
            curState[row2][col] = state1[row2][col]
    print("curState, step", row)
    print_slide(curState)


curState = [[ 0 for i in range(10)] for j in range(10)]
print("snake 1")
for row in range(len(state0)):
    print("curState, step", row)
    if row % 2 == 0:
        for col in range(len(state0[0])-1, -1, -1):
            curState[row][col] = state1[row][col]
            print_slide(curState)
            print()
    else:
        for col in range(len(state0[0])):
            curState[row][col] = state1[row][col]
            print_slide(curState)
            print()