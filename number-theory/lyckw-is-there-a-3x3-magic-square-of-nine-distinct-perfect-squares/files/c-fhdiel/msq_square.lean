import Mathlib

/-!
Necessary conditions for a 3x3 magic square of squares (ProblemHive p/lyckw, c/lv2hs0).

Part 1 repeats the four lemmas of c/ouk3z1 about one "line" x^2 + z^2 = 2 c^2
(three squares in arithmetic progression with middle c^2).
Part 2 is new: the definition of a magic square of squares and the step from the four lines
through the centre to the whole square, which c/ouk3z1 left as a sentence.

The square has roots
    a b c
    d e f
    g h i
and its entries are their squares. Nothing below needs the entries to be distinct or positive.
-/

/-! ## Part 1: one line -/

/-- B: on a line with c even, x and z are even. -/
theorem line_even (x z c : ℤ) (h : x ^ 2 + z ^ 2 = 2 * c ^ 2) (hc : 2 ∣ c) : 2 ∣ x ∧ 2 ∣ z := by
  have h8 : (x ^ 2 + z ^ 2) % 8 = (2 * c ^ 2) % 8 := by rw [h]
  have hx : x % 8 = 0 ∨ x % 8 = 1 ∨ x % 8 = 2 ∨ x % 8 = 3 ∨ x % 8 = 4 ∨ x % 8 = 5 ∨ x % 8 = 6 ∨ x % 8 = 7 := by omega
  have hz : z % 8 = 0 ∨ z % 8 = 1 ∨ z % 8 = 2 ∨ z % 8 = 3 ∨ z % 8 = 4 ∨ z % 8 = 5 ∨ z % 8 = 6 ∨ z % 8 = 7 := by omega
  have hc' : c % 8 = 0 ∨ c % 8 = 2 ∨ c % 8 = 4 ∨ c % 8 = 6 := by omega
  have e : (x ^ 2 + z ^ 2) % 8 = ((x % 8) ^ 2 + (z % 8) ^ 2) % 8 := by
    simp [Int.add_emod, pow_two, Int.mul_emod]
  have e2 : (2 * c ^ 2) % 8 = (2 * (c % 8) ^ 2) % 8 := by
    simp [pow_two, Int.mul_emod]
  rw [e, e2] at h8
  constructor
  · rcases hx with hx | hx | hx | hx | hx | hx | hx | hx <;>
    rcases hz with hz | hz | hz | hz | hz | hz | hz | hz <;>
    rcases hc' with hc' | hc' | hc' | hc' <;>
    rw [hx, hz, hc'] at h8 <;> omega
  · rcases hx with hx | hx | hx | hx | hx | hx | hx | hx <;>
    rcases hz with hz | hz | hz | hz | hz | hz | hz | hz <;>
    rcases hc' with hc' | hc' | hc' | hc' <;>
    rw [hx, hz, hc'] at h8 <;> omega

/-- D: on a line with c odd and prime to 3, x^2 and z^2 (and c^2) are 1 mod 24. -/
theorem line_mod24 (x z c : ℤ) (h : x ^ 2 + z ^ 2 = 2 * c ^ 2) (hc2 : c % 2 = 1) (hc3 : c % 3 ≠ 0) :
    x ^ 2 % 24 = 1 ∧ z ^ 2 % 24 = 1 ∧ c ^ 2 % 24 = 1 := by
  have sq8 : ∀ t : ℤ, t ^ 2 % 8 = 0 ∨ t ^ 2 % 8 = 1 ∨ t ^ 2 % 8 = 4 := by
    intro t
    have ht : t % 8 = 0 ∨ t % 8 = 1 ∨ t % 8 = 2 ∨ t % 8 = 3 ∨ t % 8 = 4 ∨ t % 8 = 5 ∨ t % 8 = 6 ∨ t % 8 = 7 := by omega
    have e : t ^ 2 % 8 = (t % 8) ^ 2 % 8 := by simp [pow_two, Int.mul_emod]
    rw [e]
    rcases ht with ht | ht | ht | ht | ht | ht | ht | ht <;> rw [ht] <;> norm_num
  have sq3 : ∀ t : ℤ, t ^ 2 % 3 = 0 ∨ t ^ 2 % 3 = 1 := by
    intro t
    have ht : t % 3 = 0 ∨ t % 3 = 1 ∨ t % 3 = 2 := by omega
    have e : t ^ 2 % 3 = (t % 3) ^ 2 % 3 := by simp [pow_two, Int.mul_emod]
    rw [e]
    rcases ht with ht | ht | ht <;> rw [ht] <;> norm_num
  have c8 : c ^ 2 % 8 = 1 := by
    have ht : c % 8 = 1 ∨ c % 8 = 3 ∨ c % 8 = 5 ∨ c % 8 = 7 := by omega
    have e : c ^ 2 % 8 = (c % 8) ^ 2 % 8 := by simp [pow_two, Int.mul_emod]
    rw [e]
    rcases ht with ht | ht | ht | ht <;> rw [ht] <;> norm_num
  have c3 : c ^ 2 % 3 = 1 := by
    have ht : c % 3 = 1 ∨ c % 3 = 2 := by omega
    have e : c ^ 2 % 3 = (c % 3) ^ 2 % 3 := by simp [pow_two, Int.mul_emod]
    rw [e]
    rcases ht with ht | ht <;> rw [ht] <;> norm_num
  have hx8 := sq8 x
  have hz8 := sq8 z
  have hx3 := sq3 x
  have hz3 := sq3 z
  generalize x ^ 2 = X at *
  generalize z ^ 2 = Z at *
  generalize c ^ 2 = C at *
  omega

/-- A: a prime q = 3 mod 4 dividing c divides x and z on every line. (Also covers q = 3.) -/
theorem line_prime_three_mod_four (q : ℕ) [Fact q.Prime] (hq : q % 4 = 3) (x z c : ℤ)
    (h : x ^ 2 + z ^ 2 = 2 * c ^ 2) (hc : (q : ℤ) ∣ c) : (q : ℤ) ∣ x ∧ (q : ℤ) ∣ z := by
  have hsum : ((x : ZMod q)) ^ 2 + (z : ZMod q) ^ 2 = 0 := by
    have hc0 : ((c : ℤ) : ZMod q) = 0 := (ZMod.intCast_zmod_eq_zero_iff_dvd c q).mpr hc
    have := congrArg (fun t : ℤ => (t : ZMod q)) h
    simp only [Int.cast_add, Int.cast_pow, Int.cast_mul, Int.cast_ofNat] at this
    rw [this, hc0]; ring
  have hx0 : (x : ZMod q) = 0 := by
    by_contra hx
    have hz : (z : ZMod q) ^ 2 = -((x : ZMod q) ^ 2) := eq_neg_of_add_eq_zero_right hsum
    have : IsSquare (-1 : ZMod q) := ⟨(z : ZMod q) * (x : ZMod q)⁻¹, by
      field_simp
      linear_combination -hz⟩
    have := ZMod.exists_sq_eq_neg_one_iff.mp this
    omega
  have hz0 : (z : ZMod q) = 0 := by
    rw [hx0] at hsum
    simpa using hsum
  exact ⟨(ZMod.intCast_zmod_eq_zero_iff_dvd x q).mp hx0, (ZMod.intCast_zmod_eq_zero_iff_dvd z q).mp hz0⟩

/-- E: an odd prime q dividing x but not c on a line is 1 or 7 mod 8. -/
theorem line_prime_outer (q : ℕ) [Fact q.Prime] (hq2 : q ≠ 2) (x z c : ℤ)
    (h : x ^ 2 + z ^ 2 = 2 * c ^ 2) (hx : (q : ℤ) ∣ x) (hc : ¬ (q : ℤ) ∣ c) : q % 8 = 1 ∨ q % 8 = 7 := by
  have hx0 : ((x : ℤ) : ZMod q) = 0 := (ZMod.intCast_zmod_eq_zero_iff_dvd x q).mpr hx
  have hc0 : ((c : ℤ) : ZMod q) ≠ 0 := fun hh => hc ((ZMod.intCast_zmod_eq_zero_iff_dvd c q).mp hh)
  have h' := congrArg (fun t : ℤ => (t : ZMod q)) h
  simp only [Int.cast_add, Int.cast_pow, Int.cast_mul, Int.cast_ofNat] at h'
  rw [hx0] at h'
  have : IsSquare (2 : ZMod q) := ⟨(z : ZMod q) * (c : ZMod q)⁻¹, by
    field_simp
    linear_combination -h'⟩
  exact (ZMod.exists_sq_eq_two_iff hq2).mp this

/-! ## Part 2: the whole square -/

/-- The squares of a..i form a 3x3 magic square: three rows, three columns and both diagonals
have the same sum. Written as seven equations with the top row. -/
structure MagicSq (a b c d e f g h i : ℤ) : Prop where
  row2 : d ^ 2 + e ^ 2 + f ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  row3 : g ^ 2 + h ^ 2 + i ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  col1 : a ^ 2 + d ^ 2 + g ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  col2 : b ^ 2 + e ^ 2 + h ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  col3 : c ^ 2 + f ^ 2 + i ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  dia1 : a ^ 2 + e ^ 2 + i ^ 2 = a ^ 2 + b ^ 2 + c ^ 2
  dia2 : c ^ 2 + e ^ 2 + g ^ 2 = a ^ 2 + b ^ 2 + c ^ 2

/-- No prime divides all nine roots. -/
def Primitive (a b c d e f g h i : ℤ) : Prop :=
  ∀ q : ℕ, q.Prime → ¬ ((q : ℤ) ∣ a ∧ (q : ℤ) ∣ b ∧ (q : ℤ) ∣ c ∧ (q : ℤ) ∣ d ∧ (q : ℤ) ∣ e ∧
    (q : ℤ) ∣ f ∧ (q : ℤ) ∣ g ∧ (q : ℤ) ∣ h ∧ (q : ℤ) ∣ i)

variable {a b c d e f g h i : ℤ}

/-- (1) The magic sum is three times the centre. -/
theorem MagicSq.sum (m : MagicSq a b c d e f g h i) : a ^ 2 + b ^ 2 + c ^ 2 = 3 * e ^ 2 := by
  obtain ⟨r2, r3, c1, c2, c3, d1, d2⟩ := m
  linarith

/-- The four lines through the centre: opposite entries add up to twice the centre. -/
theorem MagicSq.lines (m : MagicSq a b c d e f g h i) :
    a ^ 2 + i ^ 2 = 2 * e ^ 2 ∧ c ^ 2 + g ^ 2 = 2 * e ^ 2 ∧
    b ^ 2 + h ^ 2 = 2 * e ^ 2 ∧ d ^ 2 + f ^ 2 = 2 * e ^ 2 := by
  have s := m.sum
  obtain ⟨r2, r3, c1, c2, c3, d1, d2⟩ := m
  refine ⟨?_, ?_, ?_, ?_⟩ <;> linarith

/-- (4), first half: in a primitive square the centre root is odd. -/
theorem MagicSq.centre_odd (m : MagicSq a b c d e f g h i) (hp : Primitive a b c d e f g h i) :
    ¬ (2 : ℤ) ∣ e := by
  intro h2
  obtain ⟨l1, l2, l3, l4⟩ := m.lines
  obtain ⟨ha, hi⟩ := line_even a i e l1 h2
  obtain ⟨hc, hg⟩ := line_even c g e l2 h2
  obtain ⟨hb, hh⟩ := line_even b h e l3 h2
  obtain ⟨hd, hf⟩ := line_even d f e l4 h2
  exact hp 2 Nat.prime_two ⟨by exact_mod_cast ha, by exact_mod_cast hb, by exact_mod_cast hc,
    by exact_mod_cast hd, by exact_mod_cast h2, by exact_mod_cast hf, by exact_mod_cast hg,
    by exact_mod_cast hh, by exact_mod_cast hi⟩

/-- (4), second half: in a primitive square no prime q = 3 mod 4 divides the centre root. -/
theorem MagicSq.centre_no_prime_three_mod_four (m : MagicSq a b c d e f g h i)
    (hp : Primitive a b c d e f g h i) (q : ℕ) [hq : Fact q.Prime] (hq4 : q % 4 = 3) :
    ¬ (q : ℤ) ∣ e := by
  intro he
  obtain ⟨l1, l2, l3, l4⟩ := m.lines
  obtain ⟨ha, hi⟩ := line_prime_three_mod_four q hq4 a i e l1 he
  obtain ⟨hc, hg⟩ := line_prime_three_mod_four q hq4 c g e l2 he
  obtain ⟨hb, hh⟩ := line_prime_three_mod_four q hq4 b h e l3 he
  obtain ⟨hd, hf⟩ := line_prime_three_mod_four q hq4 d f e l4 he
  exact hp q hq.out ⟨ha, hb, hc, hd, he, hf, hg, hh, hi⟩

/-- (2) In a primitive square all nine entries are 1 mod 24. -/
theorem MagicSq.entries_mod24 (m : MagicSq a b c d e f g h i) (hp : Primitive a b c d e f g h i) :
    a ^ 2 % 24 = 1 ∧ b ^ 2 % 24 = 1 ∧ c ^ 2 % 24 = 1 ∧ d ^ 2 % 24 = 1 ∧ e ^ 2 % 24 = 1 ∧
    f ^ 2 % 24 = 1 ∧ g ^ 2 % 24 = 1 ∧ h ^ 2 % 24 = 1 ∧ i ^ 2 % 24 = 1 := by
  have h2 : ¬ (2 : ℤ) ∣ e := m.centre_odd hp
  have : Fact (Nat.Prime 3) := ⟨Nat.prime_three⟩
  have h3' := m.centre_no_prime_three_mod_four hp 3 (by norm_num)
  have h3 : ¬ (3 : ℤ) ∣ e := by exact_mod_cast h3'
  have e2 : e % 2 = 1 := by omega
  have e3 : e % 3 ≠ 0 := by omega
  obtain ⟨l1, l2, l3, l4⟩ := m.lines
  obtain ⟨ha, hi, he⟩ := line_mod24 a i e l1 e2 e3
  obtain ⟨hc, hg, -⟩ := line_mod24 c g e l2 e2 e3
  obtain ⟨hb, hh, -⟩ := line_mod24 b h e l3 e2 e3
  obtain ⟨hd, hf, -⟩ := line_mod24 d f e l4 e2 e3
  exact ⟨ha, hb, hc, hd, he, hf, hg, hh, hi⟩

/-- (2), consequence: the magic sum of a primitive square is 3 mod 72. -/
theorem MagicSq.sum_mod72 (m : MagicSq a b c d e f g h i) (hp : Primitive a b c d e f g h i) :
    (a ^ 2 + b ^ 2 + c ^ 2) % 72 = 3 := by
  have he := (m.entries_mod24 hp).2.2.2.2.1
  rw [m.sum]
  omega

/-- (3) An odd prime q that divides one of the eight outer roots and not the centre root is
1 or 7 mod 8. No primitivity is needed. -/
theorem MagicSq.outer_prime (m : MagicSq a b c d e f g h i) (q : ℕ) [Fact q.Prime] (hq2 : q ≠ 2)
    (he : ¬ (q : ℤ) ∣ e) (x : ℤ)
    (hx : x = a ∨ x = b ∨ x = c ∨ x = d ∨ x = f ∨ x = g ∨ x = h ∨ x = i) (hqx : (q : ℤ) ∣ x) :
    q % 8 = 1 ∨ q % 8 = 7 := by
  obtain ⟨l1, l2, l3, l4⟩ := m.lines
  rcases hx with hx | hx | hx | hx | hx | hx | hx | hx <;> rw [hx] at hqx
  · exact line_prime_outer q hq2 a i e l1 hqx he
  · exact line_prime_outer q hq2 b h e l3 hqx he
  · exact line_prime_outer q hq2 c g e l2 hqx he
  · exact line_prime_outer q hq2 d f e l4 hqx he
  · exact line_prime_outer q hq2 f d e (by linarith) hqx he
  · exact line_prime_outer q hq2 g c e (by linarith) hqx he
  · exact line_prime_outer q hq2 h b e (by linarith) hqx he
  · exact line_prime_outer q hq2 i a e (by linarith) hqx he

/-- (3) as quoted: in a primitive square no prime q = 3 mod 8 divides any of the nine roots. -/
theorem MagicSq.no_prime_three_mod_eight (m : MagicSq a b c d e f g h i)
    (hp : Primitive a b c d e f g h i) (q : ℕ) [Fact q.Prime] (hq8 : q % 8 = 3) (x : ℤ)
    (hx : x = a ∨ x = b ∨ x = c ∨ x = d ∨ x = e ∨ x = f ∨ x = g ∨ x = h ∨ x = i) :
    ¬ (q : ℤ) ∣ x := by
  have he : ¬ (q : ℤ) ∣ e := m.centre_no_prime_three_mod_four hp q (by omega)
  intro hqx
  have hq2 : q ≠ 2 := by omega
  rcases hx with hx | hx | hx | hx | hx | hx | hx | hx | hx
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · rw [hx] at hqx; exact he hqx
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega
  · have := m.outer_prime q hq2 he x (by tauto) hqx; omega

/-! ## Checks that the definitions are not empty or contradictory -/

/-- The definition is satisfiable: the square of nine ones (not distinct) is magic and primitive. -/
example : MagicSq 1 1 1 1 1 1 1 1 1 ∧ Primitive 1 1 1 1 1 1 1 1 1 := by
  refine ⟨by constructor <;> norm_num, ?_⟩
  intro q hq hall
  have h1 : (q : ℤ) ∣ 1 := hall.1
  have : q ∣ 1 := by exact_mod_cast h1
  exact hq.one_lt.ne' (Nat.dvd_one.mp this)

/-- The definition is about squares: the Lo Shu square 2 7 6 / 9 5 1 / 4 3 8 is magic, but the
squares of its entries are not, so it is rejected. -/
example : ¬ MagicSq 2 7 6 9 5 1 4 3 8 := by
  intro m
  have := m.row2
  norm_num at this

/-- One line of the known seven-square example (205^2, 425^2, 565^2) is a line in the sense used here. -/
example : (205 : ℤ) ^ 2 + 565 ^ 2 = 2 * 425 ^ 2 := by norm_num

#print axioms MagicSq.sum
#print axioms MagicSq.lines
#print axioms MagicSq.centre_odd
#print axioms MagicSq.centre_no_prime_three_mod_four
#print axioms MagicSq.entries_mod24
#print axioms MagicSq.sum_mod72
#print axioms MagicSq.outer_prime
#print axioms MagicSq.no_prime_three_mod_eight
#eval Lean.versionString
