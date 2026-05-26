"""
Process all Drive download .txt files from tool-results directory.
Maps file IDs to gallery folders, converts HEIC/JPG, saves sequentially.

Usage: python process_all_gallery.py [tool_results_dir]
"""
import json, base64, io, sys, os
from pathlib import Path

# === File ID -> gallery folder mapping ===
FOLDER_MAP = {
    # BBL
    "15zdSFAypIVVd5M4V6qpU-NyGiwOl6etz": "bbl",
    "1LtmXaAj7S8C77kcKMwUonvus6Vzw-vri": "bbl",
    "1oRETR-15sEwrEEfNe4gkO_NLRoXl2MO3": "bbl",
    "1fQEk4609y1i2bSe101z6XuCdXZua0AQW": "bbl",
    "13rEOEzESns-LKNqDnY2V8PxQKryPylQT": "bbl",
    "1hrH4FvhCf1oBogldUWu_FnK43q6pLf_6": "bbl",
    "1zxiiWxz8uFpkzsLrjUfmulvAkrugQxJw": "bbl",
    "1OQ959p6jH8UinxbozJm6ZIYZQbFfQEWe": "bbl",
    "1oq4ghdCrOBhgWuIkA_4dP07Ffodc9nKC": "bbl",
    "18rIDuvP-JqRBVu3rOBnjETuoQkV_UhNj": "bbl",
    "1PlfTdaBQRLkC0ORs-j5KTRwl2ZVDtX9E": "bbl",
    "1hIVhYZR1aDShf_i5f3On6_rLswtQjO--": "bbl",
    "1Sa-rLht9yN39UZ17Z726AwIIyM_8mVqi": "bbl",
    "1sy-Ra0MWL5uRwV5kA5xFz_JzOMPceVZW": "bbl",
    # Liposuction
    "1XouMlnxsu-8V0AsttNBnEksE8PHpVFLC": "lipo",
    "1A-Y56ziZHTviaBHKjxYwb4XFNKFbmMD7": "lipo",
    "1kqXYgGA09GyQjtX2tOoDsUEGChCFRXFb": "lipo",
    "10NHLoC_zJ7eoUIFaf7sv3lWBv7FKsr-2": "lipo",
    "16diJEOfIfj1BwMNeqSWrSu_lLQHs3CTb": "lipo",
    "1q6U40bM-cEdLIQdHcvHetqKWNyRIDl8q": "lipo",
    "16fkmTuW7Tjtyyeb8py38Vo5kof4uDuRq": "lipo",
    "1t0WVcuL3BQHydemAdrX-MUddJlsdpMnB": "lipo",
    "1G0jfr16iV_iBOfHboDybt6COEUzmbJuX": "lipo",
    "1xrWx9CAl9sXxxIhqJNlU9z-eCLtRd9V1": "lipo",
    "1-MO_jvFmTqcNKT68CPJYyUawUAvKsEBM": "lipo",
    "1dunuebUaSS7nHw-fn1ZdAgWbf3VnUFP9": "lipo",
    "1epXRm_xoCdAJZgRER0_tFS6hUG2hOwAu": "lipo",
    "1jSlFJqLF0GHAi4BgNRFVbU2Fqxans97q": "lipo",
    "1hfQraFJBPJBIJfSKzuuI0c9JSncmP4iE": "lipo",
    "1aGOWdCJpVDrwUnApkLoxq1YfiN6oK65s": "lipo",
    "1fx8QCWNKrrYmXZvLxO_Uoy9PzsbnoBV5": "lipo",
    "1AMJwNT7b62YXzuLQu-7MpefClQpwXowP": "lipo",
    "1J6CMZ493t8UNU65oURsGUwyENacu26fK": "lipo",
    "1WM-1iTTB9Ve5m0DZLWnVvMGTb-iSZeDy": "lipo",
    "1WUyEip_a-uuRcsmhD_UO5RG6tZwRgaWN": "lipo",
    "1-sVR1L25ntxkLwZUzWaRgF9cjP6862aj": "lipo",
    "1n0wmMyHFDFlE5kPiGYBOeYbIR3oHC9EW": "lipo",
    "1mxueI8iYfCIIiXFtmGi0B-tgt9mlWxxt": "lipo",
    "1I-HiAR1w_j94PB04MOiDbUJN0yeKF71u": "lipo",
    "1lPMxDHzjouCB51CfvoB1KCx2hSo08cP9": "lipo",
    "1r_rElYytaA-fdlP-NpSxOqaXF-cMMM4O": "lipo",
    "1Irn2K2dxAV-iUwtp9rAbdpC3rCuD7OB-": "lipo",
    "1DKJ0feh2zK6cfkIfC5Jo5Fgs8lRth76D": "lipo",
    "1CVW952m7VcPqS_0ek76dDceNvroLgBSy": "lipo",
    "1A6BFlzS_Ugn5Uv_TLjbsN9Nt1j74oBS0": "lipo",
    "1l3UZvitGYW6o6B2rIMPDM8tB2gjvucu5": "lipo",
    # Mastopexy
    "1_L1aGXLLQrBVrbwwzy90-_JVYve2F0kb": "mastopexy",
    "1pydoxwPmGzVMWBOU4Q07RHNizM8jhUfb": "mastopexy",
    "1o7P4P17N5Rj22smgOV4yr1oM2QHM2pCf": "mastopexy",
    "1fEU_3EncM6CsZ8HdNjlrj2Sy9kpgVGI2": "mastopexy",
    "1s_4yUpd8TNdWZHIwd5g42WfOPpB-6ei1": "mastopexy",
    "1_spEjfiFeCtjJdAFdzypWeOvQgXpS8Vy": "mastopexy",
    "1_OhDxHHxDf9Ds2WYsKbl9BSGxvrLdYLI": "mastopexy",
    "1kCp43T_aQldagke9Hd-N32VQrx8bKnsS": "mastopexy",
    "1o0KIYEMYH7C8ViwMTCqQ5tnxbXcpW9FH": "mastopexy",
    "1en4BIwPcTrhvH6pFBA2FU8FG2r9neOg2": "mastopexy",
    "1HODucvnvt-p7F7Jv-JtCFdjqp6FTLNQv": "mastopexy",
    "15FHtRBRWTKshT-VOlciVIDTRtDCXJ5L9": "mastopexy",
    "1kvUz7RPwNw3kvTz-ARoFjfgR89ZBaip3": "mastopexy",
    "1wOEAs4rHe4YHasrSKH-Nj4OoTG9HyZxn": "mastopexy",
    "13jvipx7YDABGarkowSpW85TkIg4FpknI": "mastopexy",
    "17JGLUHUN84XKkbcg1jgvJMae4-3UvlEH": "mastopexy",
    "14ukGlPT2HkDSi8hRpvP4GJzfEYn8ajT8": "mastopexy",
    # Tummy Tuck
    "1cVqydCVqLPWVjpFCLfve2olRc85ZL-7z": "tummy-tuck",
    "1GGcoPZ6SbpEDwXNSb_kpnnvyHg6ardcB": "tummy-tuck",
    "1Wbi823Dny5OAfrCryrwpjx1ypMrjA7D7": "tummy-tuck",
    "1vQqp765IusjGumFqU_TvoTPI8RKrPWC4": "tummy-tuck",
    "1Qm3BGOcbBQoJtiyVwgSvJMHAmppU9gkm": "tummy-tuck",
    "1Nq1SBCpGuKNTC9z8nIxGXK_xWFWSoN-L": "tummy-tuck",
    "1Ji8g9A2G_hZOurgFacINVj1Lu4X2D0RC": "tummy-tuck",
    "1qkhoonZdnIXlv68mc3Bns3Hnr4LJrPYF": "tummy-tuck",
    "1LDkZoUHS1mU0ckvAvG-vPaQUaq_BUXl0": "tummy-tuck",
    # Augmentation
    "1gowRcTKBmoN_hTK_lndTn3SkREoH3pn6": "augmentation",
    "1oy2q9GResxj_fp5-uU7lLbCt6ZxQ6Fq0": "augmentation",
    "1A47imX_qc21P3hqrYscXmfqBK38LNwZF": "augmentation",
    "1ZiyiJdIeX9tKoRlgWlyZ_uSTc6hPSskx": "augmentation",
    "1vuWv1QOMhLmAVhTiBOQCnAtreQTf-SFW": "augmentation",
    "1aE56EMPFS5ehBMytdm_cC5MGMnHlZKoR": "augmentation",
    "1LH3rhlrrLX7y7A0GclIeXy7VqfOk1Jbp": "augmentation",
    "1nYZdiW86CoQtROT47zYzUQASKKKllpsR": "augmentation",
    "1kO_IlR3DhjvWwjrkJQ7Ltm1axscCyj0D": "augmentation",
    "1Aet5dQEVHOvcvvULp0fnsul5t5HeOCfC": "augmentation",
    "1UwICaZKIVihj-C2fsDBsSsP8YrVcGNHO": "augmentation",
    "1ddWj5Qcfl6JrCwzQVYr0Ob0SvOMPPqsX": "augmentation",
    "1ausPoktpHzf3H3M0Sad_m6XjgjOE9tXh": "augmentation",
    "18M1mUeFrlJI5F_eGEsBy6gJOlgtTFBq7": "augmentation",
    "1YbdzICSknCa6zSX3sV9g6Qm9poq1K6zc": "augmentation",
    "1Uid9A5q74FlMgoe1OswWA97AyuWDDAgA": "augmentation",
    "1lIP2l0XAI1JI9mgaDYgHNImT2c3i1Ygm": "augmentation",
    "1dA5zczCtbSvGFjSKYRnX14GCUfb9ajvF": "augmentation",
    "1GEMfm4EP4jEnJr6XmJieH416eI7fYwPK": "augmentation",
    "1PbFCFos46QLzc4hijNPC8l5OmnZmYbnQ": "augmentation",
    "1UbdxEjvFwQCFscvFsMx4O44xta7vXSyu": "augmentation",
    "18-uqe1NdXAmeHyi6BlcXhgOopZNgBSlH": "augmentation",
    # Reduction Mammoplasty
    "1KrWVu2bk7NaPT1hPC92nGRPbOjAG2WR3": "reduction",
    "1JRex_uSPdtxIJ6RL_lRGhZuNTjWpodsY": "reduction",
    "16-H5_v1AmsGvO3EAxyxkHX4lY6-5BQsC": "reduction",
    "1-g4I6x_5ypovEHZEcyC92w6MZ4bfpasi": "reduction",
    "1TuLaHiIeim-kKoRPmYLE1meS5jjaLp7p": "reduction",
    "1P30ezppeMb8TlD00tvnNer-UgYdMdzQ1": "reduction",
    "1FAWF2u1qKaRr6pEeMvEnGplCGnztka_x": "reduction",
    "1sdkYKdxZsNu1V2O4hlFFrC083xenDUIj": "reduction",
    "1asFUBNJnGkjUvxqaqCqnbKy2ZeyEiNBw": "reduction",
    "1pKKKrjHV3mVRA7cuRzA3zqfoVm57zXQK": "reduction",
    "1GGJih1WS4T7UbgGTjNH8GLEV-yER8Pyn": "reduction",
    "118jFvThz1O_XijPss5TPoBkhnzY0QBf7": "reduction",
    "1RdSNiIF_xX1G7wt-Cb3NAxOpoo34mh9j": "reduction",
    "1jKc8o2Nhud4Oqqklu-08jeCAu06aXhrH": "reduction",
    "1EQIdNpuN90R9XftU963bAetMjW8MJQ_T": "reduction",
    "1l5nv5t46M_4lRcRt-BdmrDD8shyOBXE-": "reduction",
    "1FuVFtdV979Uk7PXcyeo0ICzUN6BJmBkm": "reduction",
    "1DrK1kFQi1kk1yAQ1-5MXs8CNGdarTOA2": "reduction",
    # Neck Lift
    "1ISrE2oRuNJ14TyDwxM2V0JdebmV8q7z-": "neck-lift",
    "12Fixh_jlM4TgaOd73gKQIZzzp4UPv9-u": "neck-lift",
    "1JkgRtSE7y_sCkR68yj8iF8p0Z0VPyFJw": "neck-lift",
    "1mSQBUDzs5_cdP2hd2Z6MCvckgwn_5s7R": "neck-lift",
    "1hYleTJ5meRJKQLtrwrDkPzhhysyx5KCp": "neck-lift",
    "12O9FOOV6vhms3UiyhMSRoRK8AWhAJYtP": "neck-lift",
    "1_bvfMXd1i19HIgna4ei4t8uS_myyhZ2V": "neck-lift",
    "1ndpMx13P3X2aZsrKCn0I6C0t0gzr8nPb": "neck-lift",
    # Rhinoplasty
    "1uenJLN-js4KPAjmn2sj0gKs11mcRk0x8": "rhinoplasty",
    "1DckY5zfx83TARm8QVyTe2-062hxp-GuF": "rhinoplasty",
    # Dr Matwa Photos
    "1d-tVHnhxzw4e90HzOF2IvbZ6LRyO_Jx9": "dr-matwa",
    "1KErM8S3hmiD9OyQ5xHpJFt7ThhsnZlyS": "dr-matwa",
    # Otoplasty
    "1RQJcOWEYC_ocQJZYesO2-DcGB0oKjGG-": "otoplasty",
    "1c8-dOj2VDexvFtr4l7IKWrmV5VOkNU76": "otoplasty",
    "1YSb9k8uGYv1bj3JAePKZYb26aKraV0Eg": "otoplasty",
    "1rug5frF4vcHDJcqEYFBQIE0GzH7_bFdc": "otoplasty",
    "1f0deF8j9jkvmiBCv8v5x7tH15OpnQTM_": "otoplasty",
    "1nQX4aNIp7NurH3BJvm5W_BW3J9j7AQSI": "otoplasty",
    "1hXm5ejfvtm7xYR7ZNHtRxpqOx59plTp5": "otoplasty",
    "12PwIpS85tWCRoSgZQZrHDpjOF7SemzV2": "otoplasty",
    # Blepharoplasty
    "11DJIGLRuKlangjRdRShTbX6xHRS-hihQ": "blepharoplasty",
    "1XX6TmSj8hakRTuVOV3gJOcN1DbBzPSxz": "blepharoplasty",
    "1seksFUCV8DIT7BgUlr2fFIuP0wL56KHF": "blepharoplasty",
    "1BOKkplMLiVyQd0HY0uko4LsScz1by-PX": "blepharoplasty",
    # Facelift
    "1VOfPTb2EsGk8SxZRfjiDiqKmXpiLH659": "facelift",
    "1vuU20DIxngHGgv80ZPKocGEPcO0Ox2mn": "facelift",
    "1fQhe0dsOMxSkVsfcphSrKlN1_jtHXxL7": "facelift",
    "17n-yvGyIbGB4gEEbEAvtzOk6bq1kYh-v": "facelift",
    # Regional Liposuction
    "1_jHjdM3lwUDCjB1Eyrnn-F62G9lmM0z6": "reg-lipo",
    "13u6jXwyvgbMHAzAalUM-hOUP_q-dBMs3": "reg-lipo",
    "102tGtnf6mgBFH3STe-GJ_DSYlX_UoKYJ": "reg-lipo",
    "1Qvt0ue7BOli46ZewGHjLiNv5FzNBnBpQ": "reg-lipo",
    # Clitoroplasty (FGM)
    "1hQS4ghuKedgpgMijGQeP6CioglMkCWFk": "clitoroplasty",
    "18mj-2zaDWenwM-y8HbVy7uFwmNGCHszH": "clitoroplasty",
    # Mummy Make-over
    "1bSi410lN5SLk6qxAcCpEKFdbPkSSizLL": "mummy-makeover",
    "1lcydw92tMySh8d6dLdCea5xNlwJiNsk9": "mummy-makeover",
    "1YavWdhpRpFsuC0ykHPtvGHTqaFuGPGCR": "mummy-makeover",
    "1eI0GisWu_7FOSPwhwVTDQytPJUxfQP3Y": "mummy-makeover",
    # Home Page Running Photos
    "1Ysy-IQYRb_mzhbOTjAltA067XUb-eQge": "running",
    "1asV-VOup1paMI1Lort2uT1ogCqtgXXOX": "running",
    "1ljq78O9ahcXu0n5PM2_CNXZ1nicNxi7E": "running",
    "1l7CN3TQUw3gYWEuDgS2qrfdFr_NPr3TH": "running",
    "1z8rVrMLHNyN1PDCorQkoelwsR9pJRu_S": "running",
    "1SCM4Q-dPAmgUJ8hMMPsDhBMKddeV6iEm": "running",
    "1lc9Ow0VRv0gQAB-SfaUykBqhp1wpNvY3": "running",
    "1HnNHwRrUJ3h2_mvdT4S0IIO4SnB5QOJ9": "running",
    "16GZxeJIi7onkAOk946qo73iVK6Fezi2z": "running",
    "1uVEdIUeZILubsnz2tx1mFNsjDKyL38-S": "running",
    "1YEVz6OXgRuX98gcMPZ-hsWuIWSGrvJda": "running",
    "1W4_F4CG8HET_XQDg8bbzw73mNYkWmt3J": "running",
    "1Pu1F4Efvjs4CXW9pa2ZPzyMuHYcFBFde": "running",
    "19jTZQ_5o-bzRt3y5G7U65M48aScGLdG6": "running",
    "1CG7Y3pJVQUwcsudQ_vlRmAKK5ESqy9BJ": "running",
    "1CyUXAjzfV0jBce783_XyCwYoSMdCIDha": "running",
    "1JXwt5Rkkhx-ZXWbXdckGFczwH_tqU-yW": "running",
}

GALLERY_BASE = Path(r"C:\Users\Joel\Website Designs\truffel-healthcare\images\gallery")
IMAGES_BASE  = Path(r"C:\Users\Joel\Website Designs\truffel-healthcare\images")
# Folders that go directly under images/ rather than images/gallery/
DIRECT_FOLDERS = {"dr-matwa", "running"}
MAX_W, MAX_H = 900, 1100

def next_seq(folder: Path) -> int:
    """Return next sequential number (1-based) for a gallery folder."""
    existing = [f for f in folder.glob("*.jpg")]
    nums = []
    for f in existing:
        try:
            nums.append(int(f.stem))
        except ValueError:
            pass
    return max(nums, default=0) + 1

def process_txt(txt_path: Path) -> bool:
    """Process one tool-result .txt file. Returns True if saved."""
    from pillow_heif import register_heif_opener
    register_heif_opener()
    from PIL import Image

    try:
        raw = txt_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        print(f"  SKIP {txt_path.name}: parse error - {e}")
        return False

    file_id = data.get("id", "")
    folder_name = FOLDER_MAP.get(file_id)
    if not folder_name:
        return False  # Not a gallery image

    b64 = data.get("content", "")
    if not b64:
        print(f"  SKIP {txt_path.name}: no content")
        return False

    base = IMAGES_BASE if folder_name in DIRECT_FOLDERS else GALLERY_BASE
    folder = base / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    seq = next_seq(folder)
    out_path = folder / f"{seq:02d}.jpg"

    try:
        raw_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(raw_bytes))
        img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(str(out_path), "JPEG", quality=85, optimize=True)
        print(f"  OK {folder_name}/{out_path.name}  {img.size}  ({out_path.stat().st_size // 1024} KB)  [{file_id[:12]}...]")
        return True
    except Exception as e:
        print(f"  ERROR {txt_path.name}: {e}")
        return False

def main():
    tool_results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not tool_results_dir:
        print("Usage: python process_all_gallery.py <tool_results_dir>")
        sys.exit(1)

    txt_files = sorted(tool_results_dir.glob("*download_file_content*.txt"))
    print(f"Found {len(txt_files)} download txt files in {tool_results_dir}")

    saved = 0
    skipped = 0
    for f in txt_files:
        result = process_txt(f)
        if result:
            saved += 1
        else:
            skipped += 1

    print(f"\nDone: {saved} saved, {skipped} skipped/unknown")

    # Print gallery summary
    print("\nGallery summary:")
    for folder in sorted(GALLERY_BASE.iterdir()):
        if folder.is_dir():
            count = len(list(folder.glob("*.jpg")))
            print(f"  {folder.name}: {count} images")

if __name__ == "__main__":
    main()
