import zipfile, os, pathlib

def extract_all_images_fast(pptx_path, out_dir="extracted_images"):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pptx_path) as z:
        for m in z.namelist():
            if m.startswith("ppt/media/"):
                z.extract(m, out)
    print(f"Done. Check {out / 'ppt' / 'media'}")
    
#extract_all_images_fast("assets/templates/professional.pptx")
extract_all_images_fast("assets/templates/elementary.pptx")
extract_all_images_fast("assets/templates/middle.pptx")
extract_all_images_fast("assets/templates/whitelabel.pptx")