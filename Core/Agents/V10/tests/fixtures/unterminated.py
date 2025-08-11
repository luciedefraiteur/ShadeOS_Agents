# Unterminated scope at EOF

def broken(x):
    v = 0
    for i in range(x):
        v += i
# no dedent here — EOF
