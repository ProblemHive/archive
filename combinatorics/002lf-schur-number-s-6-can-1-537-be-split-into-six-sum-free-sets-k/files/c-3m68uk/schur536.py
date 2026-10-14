# Check the six-set sum-free partition of 1..536 printed on page 6 of
# Fredricksen and Sweet, Electronic Journal of Combinatorics 7 (2000) #R32.
# The paper lists only the smaller member of each pair {i, 537 - i}; the other member
# is in the same set. Exception stated in the paper: 179 = 537/3 and 358 = 2*537/3
# may be in different sets (179 is listed in set 4, 358 in set 1).
N = 536
half = {
 1: """1 5 8 11 14 24 27 30 33 36 40 43 46 49
 52 65 71 77 81 84 90 93 99 103 109 112 115 125 128 131
 134 137 144 147 150 153 160 163 166 169 172 181 185 188 191 194
 201 204 207 213 220 223 226 229 232 235 238 242 245 248 251 254
 264 267 358""",
 2: """2 12 19 25 26 34 41 57 58 63 72 79 85 86
 95 96 102 118 123 124 140 141 145 146 155 156 162 173 183 193
 200 206 211 215 216 222 233 239 244 253 260 261 266""",
 3: """3 10 16 22 23 29 35 42 48 56 60 62 67 68
 69 74 75 80 87 88 94 100 101 106 107 113 114 119 121 126
 133 139 151 152 158 159 164 165 171 178 184 192 197 198 203 205
 210 217 237 241 243 249 250 255 256""",
 4: """4 13 20 28 31 38 50 61 64 73 83 91 98 108
 110 117 120 132 135 142 143 154 161 168 177 179 187 195 209 212
 214 219 221 224 231 236 246 258 265""",
 5: """6 9 17 21 32 39 44 51 54 55 66 70 82 89
 92 104 111 127 129 130 149 167 175 189 190 202 225 227 247 252
 262 263""",
 6: """7 15 18 37 45 47 53 59 76 78 97 105 116 122
 136 138 148 157 170 174 176 180 182 186 196 199 208 218 228 230
 234 240 257 259 268""",
}
col = [0] * (N + 1)
problems = []
for c, text in half.items():
    for x in map(int, text.split()):
        for y in ((x,) if x in (179, 358) else (x, N + 1 - x)):
            if col[y]:
                problems.append(f"{y} listed twice")
            col[y] = c
missing = [i for i in range(1, N + 1) if col[i] == 0]
viol = [(x, y, x + y) for x in range(1, N + 1) for y in range(x, N + 1 - x)
        if col[x] == col[y] == col[x + y]]
print("numbers 1..536 coloured:", N - len(missing), "missing:", missing, "problems:", problems)
print("set sizes:", [col.count(c) for c in range(1, 7)])
print("monochromatic x + y = z with x <= y:", len(viol), viol[:5])
print("asymmetric pairs i, 537-i:", [(i, N + 1 - i) for i in range(1, 269) if col[i] != col[N + 1 - i]])
print("smallest element of each set:", [col.index(c) for c in range(1, 7)])
s = "".join("ABCDEF"[c - 1] for c in col[1:])
print("colouring of 1..536 (A = set 1, ..., F = set 6):")
for i in range(0, N, 67):
    print(s[i:i + 67])
# Which sets could take 537? Count the pairs x + y = 537 (x < y) inside each set.
cnt = {c: 0 for c in range(1, 7)}
for x in range(1, 269):
    if col[x] == col[537 - x]:
        cnt[col[x]] += 1
print("pairs x + (537 - x) inside each set (blocks 537 from that set):", cnt)
# For each n > 536: is the colouring extendable by one number?
free = [c for c in range(1, 7) if not any(col[x] == c and col[537 - x] == c for x in range(1, 269))]
print("sets that can take 537 without any change:", free)
