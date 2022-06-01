one fifth size
---------------
sf = 0.2 (rel. to size of sprites original fish bundle)
frame w x h = (88, 56)
sheet w x h = 1760 x 2016 (~0.85MB)
row x cols = 20 x 36

format:
cols = animation sequence
rows = colours x states x directions

where 
colours = B(0), G(1), O(2), P(3), R(4), Y(5)
states = idle(0) (20 frames), swim(1) (16 frames), swim-chomp(2) (16 frames)
directions = left(0), right(1)

Access formula for frame toplefts (0-indexed):
x = animationFrame * 88
y = num_states * num_directions * icolour + (num_states-1)*istate + (num_dirns-1)*idirn = 6*icolour + 2*istate + idirn

e.g orange (icol=2), swim-chomp (istate=2), right(idirn=1) --> y = 6*2 + 2*2 + 1 = 11


Note:
FishTypes 01, 04, 05 don't have swim-chomp frames (those frames will be blank in spritesheet)

Image frame sizes (generally smaller than actual frame size)
IMAGE_SIZES = {"01": (75, 56), "02": (59, 50), "03": (79, 53), "04": (43, 29), "05": (88, 56), "06": (63, 56)}"



