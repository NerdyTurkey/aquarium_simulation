one third size
------------------
sf = 0.33 (rel. to size of sprites original fish bundle)
frame w x h = (146, 93)
sheet w x h = 2920 x 3348 (~1.6MB)
row x cols = 20 x 36

format:
cols = animation sequence
rows = colours x states x directions

where 
colours = B(0), G(1), O(2), P(3), R(4), Y(5)
states = idle(0) (20 frames), swim(1) (16 frames), swim-chomp(2) (16 frames)
directions = left(0), right(1)

Access formula for frame toplefts (0-indexed):
x = animationFrame * 146
y = num_states * num_directions * icolour + (num_states-1)*istate + (num_dirns-1)*idirn = 6*icolour + 2*istate + idirn

e.g orange (icol=2), swim-chomp (istate=2), right(idirn=1) --> y = 6*2 + 2*2 + 1 = 11


Note:
FishTypes 01, 04, 05 don't have swim-chomp frames (those frames will be blank in spritesheet)

Image frame sizes (generally smaller than actual frame size)
IMAGE_SIZES = {"01": (124, 93), "02": (97, 83), "03": (130, 88), "04": (71, 49), "05": (146, 92), "06": (104, 92)}



