import os

# C: drive is full, completely reroute Argos Translate package downloads to D:
os.environ["ARGOS_PACKAGES_DIR"] = r"D:\temp\argos_packages"
os.environ["XDG_DATA_HOME"] = r"D:\temp\argos_data"

# Also reroute all Python temporary file downloads to D: drive (downloads stage here first!)
os.environ["TMP"] = r"D:\temp"
os.environ["TEMP"] = r"D:\temp"

import argostranslate.package
import argostranslate.translate
import tempfile

# Force Python's tempfile to D:\temp because os.environ changes happen too late (uvicorn already imported tempfile)
tempfile.tempdir = r"D:\temp"

_packages_installed = set()

def _ensure_package(from_code: str, to_code: str):
    key = f"{from_code}-{to_code}"
    if key in _packages_installed:
        return
        
    installed_packages = argostranslate.package.get_installed_packages()
    if any(pkg.from_code == from_code and pkg.to_code == to_code for pkg in installed_packages):
        _packages_installed.add(key)
        return

    print(f"[Translation] Downloading {from_code}->{to_code} language package (this only happens once)...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        ), None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
        _packages_installed.add(key)
        print(f"[Translation] Installed {key} successfully.")
    else:
        raise ValueError(f"Language translation {from_code} -> {to_code} not available in Argos.")

def translate_text(text: str, target_lang: str = "hin_Deva", source_lang: str = "eng_Latn") -> str:
    """
    Translates text locally using Argos Translate (CTranslate2 backend).
    This memory-safe approach doesn't crash Windows like Transformers sometimes can.
    """
    if not text.strip():
        return ""
        
    # Map from NLLB tag to Argos tag
    lang_map = {
        "hin_Deva": "hi",
        "mar_Deva": "mr",
        "fra_Latn": "fr",
        "spa_Latn": "es",
        "eng_Latn": "en"
    }
    
    from_code = lang_map.get(source_lang, "en")
    to_code = lang_map.get(target_lang, "hi")
    
    _ensure_package(from_code, to_code)
    
    print(f"[Translation] Translating to {to_code}...")
    
    # Simple chunking to avoid extreme sentences
    paragraphs = [p for p in text.replace("\n\n", "\n").split(". ") if p.strip()]
    translated = []
    
    for p in paragraphs:
        if len(p.strip()) < 2:
            continue
        # Argos translate method
        res = argostranslate.translate.translate(p, from_code, to_code)
        translated.append(res)
        
    return ". ".join(translated) + ("." if text.strip().endswith(".") else "")
