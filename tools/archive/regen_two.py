from generate_backgrounds import generate_background, BACKGROUNDS
for name in ["trophy_spotlight", "golden_arena"]:
    generate_background(name, BACKGROUNDS[name], overwrite=True)
