import os
import requests
from tqdm import tqdm

CMS_BASE = "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads/"
ALT_2010_BASE = "https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/SynPUFs/Downloads/"

YEARS = [2008, 2009, 2010]
SAMPLES = [f"Sample_{i}" for i in range(1, 21)]

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def download(url, out_path):
    if os.path.exists(out_path):
        print(f"✔ Exists, skipping: {out_path}")
        return

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise requests.HTTPError(f"{r.status_code} {url}")

    total = int(r.headers.get("content-length", 0))
    with open(out_path, "wb") as f, tqdm(
        desc=os.path.basename(out_path),
        total=total,
        unit="B",
        unit_scale=True,
    ) as bar:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
            bar.update(len(chunk))


# -------------------------------------------------
# Beneficiary Summary Files (2008–2010)
# -------------------------------------------------
def download_beneficiary_files():
    for year in YEARS:
        for sample in SAMPLES:

            filename = f"DE1_0_{year}_Beneficiary_Summary_File_{sample}.zip"

            # Known CMS typo: 2010 Sample_10
            if year == 2010 and sample == "Sample_10":
                url = ALT_2010_BASE + filename
            else:
                url = CMS_BASE + filename

            out = os.path.join(DATA_DIR, filename)

            try:
                download(url, out)
            except Exception as e:
                print(f"⚠ Skipped: {filename} ({e})")


# -------------------------------------------------
# Inpatient Claims (partitioned by Sample)
# -------------------------------------------------
def download_inpatient_claims():
    for sample in SAMPLES:
        filename = f"DE1_0_2008_to_2010_Inpatient_Claims_{sample}.zip"
        url = CMS_BASE + filename
        out = os.path.join(DATA_DIR, filename)

        try:
            download(url, out)
        except Exception as e:
            print(f"⚠ Skipped: {filename} ({e})")


if __name__ == "__main__":
    download_beneficiary_files()
    download_inpatient_claims()

