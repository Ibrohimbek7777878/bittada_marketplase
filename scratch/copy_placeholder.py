import shutil
import os

src = "/home/ibrohim/.gemini/antigravity/brain/03323779-1d12-4325-94c8-e711a4739179/placeholder_mebel_1777553595439.png"
dst = "/home/ibrohim/Desktop/client_baza/bittada_marketplase/backend/static/images/placeholder.png"

os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy(src, dst)
print(f"Copied {src} to {dst}")
