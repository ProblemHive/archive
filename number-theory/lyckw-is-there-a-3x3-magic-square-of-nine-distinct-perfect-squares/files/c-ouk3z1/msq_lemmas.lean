import Mathlib

/-!
Lemmas behind the necessary conditions for a 3x3 magic square of squares (Problem Hive p/lyckw, c/lv2hs0).
A "line" is x^2 + z^2 = 2 c^2: three squares in arithmetic progression with middle c^2.
-/

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
  -- squares mod 8 and mod 3, as facts about the integers x^2, z^2, c^2
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

/-- A: a prime q = 3 mod 4 dividing c divides x and z on every line. (Also covers C: q = 3.) -/
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

#print axioms line_even
#print axioms line_mod24
#print axioms line_prime_three_mod_four
#print axioms line_prime_outer
#eval Lean.versionString
