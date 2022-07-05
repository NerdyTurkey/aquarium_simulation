from random import choices
prob_chomp = 0.2
num_chomps = 0
n = 1000
for i in range(n):
    c = choices((None, "chomp"), weights=(prob_chomp, 1 - prob_chomp))[0]
    if c == "chomp":
        num_chomps +=1
print(num_chomps/n)