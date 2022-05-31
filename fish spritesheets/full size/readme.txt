full size
----------
sf = 1.0 (rel to raw fish bundle sprites)
frame w x h = 444 x 283
sheet w x h = 8880 x 10188 (~6MB)
row x cols = 20 x 36

format:
cols = animation sequence
rows = colours x states x directions

where 
colours = B(0), G(1), O(2), P(3), R(4), Y(5)
states = idle(0) (20 frames), swim(1) (16 frames), swim-chomp(2) (16 frames)
directions = left(0), right(1)

Access formula for frame toplefts (0-indexed):
x = animationFrame * 444
y = num_states * num_directions * icolour + (num_states-1)*istate + (num_dirns-1)*idirn = 6*icolour + 2*istate + idirn

e.g orange (icol=2), swim-chomp (istate=2), right(idirn=1) --> y = 6*2 + 2*2 + 1 = 11

Note:
FishTypes 01, 04, 05 don't have swim-chomp frames (those frames will be blank in spritesheet)

Image frame sizes (generally smaller than actual frame size)
01: 376 x 283 
02: 295 x 253
03: 396 x 269
04: 216 x 149
05: 444 x 281
06: 318 x 280
