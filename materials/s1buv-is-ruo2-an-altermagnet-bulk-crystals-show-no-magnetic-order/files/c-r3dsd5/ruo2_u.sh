#!/bin/bash
# Nonmagnetic (NM) against altermagnetic (AM: Ru1 up, Ru2 down) rutile RuO2 in PBE+U,
# Quantum ESPRESSO pw.x, PAW pseudopotentials from pslibrary 1.0.0 (in /data/s1buv).
# Structure: experimental a = 4.492 A, c = 3.106 A, u = 0.306 (XRD values as tabulated in
# arXiv:cond-mat/0309714), optionally with in-plane strain eps_a and c scaled by eps_c.
# Usage: [K="8 8 12" ECW=50 ECR=400 CT=1d-9] ./ruo2_u.sh U [eps_a] [eps_c]
#   (U in eV on Ru 4d, ortho-atomic projectors; K k-mesh, ECW/ECR cutoffs in Ry, CT scf threshold)
# Prints: U eps_a eps_c E_NM E_AM (Ry) dE = E_AM - E_NM (meV per formula unit) and |m_Ru|.
set -e
U=$1; EA=${2:-0}; EC=${3:-0}; K=${K:-"8 8 12"}; ECW=${ECW:-50}; ECR=${ECR:-400}; CT=${CT:-1d-9}
A=$(python3 -c "print(4.492*(1+$EA))"); C=$(python3 -c "print(3.106*(1+$EC))"); u=0.306
mkdir -p tmp; tag="U${U}_a${EA}_c${EC}_k${K// /}_e${ECW}"
common() {
cat <<EOF
&control
  calculation='scf', prefix='$1_$tag', outdir='./tmp', pseudo_dir='/data/s1buv'
/
&system
  ibrav=6, celldm(1)=$(python3 -c "print($A/0.529177210903)"), celldm(3)=$(python3 -c "print($C/$A)"),
  nat=6, ntyp=3, ecutwfc=$ECW, ecutrho=$ECR,
  occupations='smearing', smearing='mv', degauss=0.01,
  nspin=$2, starting_magnetization(1)=0.5, starting_magnetization(2)=-0.5,
  lda_plus_u=.true., lda_plus_u_kind=0, U_projection_type='ortho-atomic',
  Hubbard_U(1)=${U}d-30, Hubbard_U(2)=${U}d-30
/
&electrons
  conv_thr=$CT, mixing_beta=0.3
/
ATOMIC_SPECIES
Ru1 101.07 Ru.pbe-spn-kjpaw_psl.1.0.0.UPF
Ru2 101.07 Ru.pbe-spn-kjpaw_psl.1.0.0.UPF
O   15.999 O.pbe-n-kjpaw_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
Ru1 0.0 0.0 0.0
Ru2 0.5 0.5 0.5
O  $u $u 0.0
O  -$u -$u 0.0
O  $(python3 -c "print(0.5+$u)") $(python3 -c "print(0.5-$u)") 0.5
O  $(python3 -c "print(0.5-$u)") $(python3 -c "print(0.5+$u)") 0.5
K_POINTS automatic
$K 0 0 0
EOF
}
# Hubbard_U is given in eV in QE 6.7 (old input syntax)
URY=$U
common NM 1 | sed "s/${U}d-30/$URY/g" > nm_$tag.in
common AM 2 | sed "s/${U}d-30/$URY/g" > am_$tag.in
mpirun --allow-run-as-root -np $PHS_CPUS pw.x -nk 4 -in nm_$tag.in > nm_$tag.out
mpirun --allow-run-as-root -np $PHS_CPUS pw.x -nk 4 -in am_$tag.in > am_$tag.out
enm=$(grep '^!' nm_$tag.out | tail -1 | awk '{print $5}')
eam=$(grep '^!' am_$tag.out | tail -1 | awk '{print $5}')
mag=$(grep -A2 'Magnetic moment per site' am_$tag.out | tail -2 | head -1 | awk '{print $NF}')
[ -z "$mag" ] && mag=$(grep 'magn=' am_$tag.out | tail -2 | head -1 | sed 's/.*magn=\s*//' | awk '{print $1}')
python3 -c "print('U %s eps_a %s eps_c %s  E_NM %s  E_AM %s Ry  dE %.2f meV/f.u.  m_Ru %s' % ('$U','$EA','$EC','$enm','$eam',($eam-($enm))*13605.693122994/2, '$mag'))"
