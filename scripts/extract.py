#!/usr/bin/env python
import os
import sys
import base64
import subprocess
import re

fingerprints = []
totalCerts = 0
certNr = 1

def main(file1, file2):
    global totalCerts

    # Check if OpenSSL supports the CMS command
    out, err = execute("openssl cms")
    if err.decode().find("'cms' is an invalid command") != -1:
        print("The version of OpenSSL you are using doesn't support the CMS command")
        print("You need to get a version that does (e.g., from Homebrew)")
        exit(1)

    # Remove old master list if it exists
    if os.path.exists("masterList.pem"):
        os.remove("masterList.pem")

    # Process the first file
    print(f"Processing file: {file1}")
    process_file(file1)

    # Process the second file
    print(f"Processing file: {file2}")
    process_file(file2)

    print("====================================")
    print(f"Created masterList.pem containing {totalCerts} certificates")

def process_file(filename):
    global totalCerts, certNr

    # Identify the type of file
    if filename.lower().endswith(".ldif"):
        # Read and parse LDIF file
        cns, masterLists = readAndExtractLDIFFile(filename)
    elif filename.lower().endswith(".ml"):
        masterLists = readInMasterListFile(filename)
        cns = ["MasterList ml file"]
    else:
        print(f"Unsupported file format: {filename}")
        return

    print(f"Read in {len(masterLists)} masterlist files from {filename}")
    if filename.lower().endswith(".ldif"):
        print(f"Read in {cns} CNS")

    for index, ml in enumerate(masterLists):
        certNr = 1
        print("-----------------------------------")
        if filename.lower().endswith(".ldif"):
            print(f"Verifying and extracting MasterList {index} - {cns[index]}")
        try:
            extractCertsFromMasterlist(ml)
        except Exception as e:
            print("Error extracting certs from masterlist")
            print("Skipping this masterlist - certs from this list will not be included.")

def readAndExtractLDIFFile(file):
    adding = False
    certs = []
    cns = []
    cn = ""
    with open(file, "r") as inf:
        cert = ""
        for line in inf:
            if line.startswith("cn: "):
                cn = line[4:]
            elif line.startswith("CscaMasterListData:: ") or line.startswith("pkdMasterListContent:: "):
                cert = line[21:]
                adding = True
            elif not line.startswith(" ") and adding:
                adding = False
                certs.append(cert)
                cns.append(cn)
                cert = ""
            elif adding:
                cert += line
        if cert != "":
            certs.append(cert)
            cns.append(cn)

    print(f"Read {len(certs)} certs from {file}")
    masterLists = []
    for cert in certs:
        data = base64.b64decode(cert)
        masterLists.append(data)

    return cns, masterLists

def readInMasterListFile(file):
    with open(file, "rb") as inf:
        data = inf.read()

    return [data]

def extractCertsFromMasterlist(masterList):
    global totalCerts

    # Run openssl cms to verify and extract the signed data
    cmd = "openssl cms -inform der -noverify -verify"
    signedData, err = execute(cmd, masterList)

    err = err.decode("utf8").strip().replace("CMS ", "")

    if err != "Verification successful":
        print(f"[{err}]")
        raise Exception("Verification of Masterlist data failed")

    print("MasterList Verification successful")

    certList = extractPEMCertificates(signedData)

    print("Removing duplicates")
    uniqueCerts = [x for x in certList if uniqueHash(x)]

    print(f"Removed {len(certList) - len(uniqueCerts)} duplicate certificates")
    totalCerts += len(uniqueCerts)

    # Append to masterList.pem
    with open("masterList.pem", "ab") as f:
        for c in uniqueCerts:
            f.write(c)

def extractPEMCertificates(signedData):
    global certNr
    print("Extracting all certificates from payload")
    cmd = "openssl asn1parse -inform der -i"
    data, err = execute(cmd, signedData)

    lines = data.decode("utf8").strip().split("\n")
    valid = False
    certs = []

    certCount = len([i for i in lines if "d=2" in i])
    for line in lines:
        if re.search(r":d=1", line):
            valid = False
        if re.search(r"d=1.*SET", line):
            valid = True
        if re.search(r"d=2", line) and valid:
            # Parse line
            match = re.search(r"^ *([0-9]*).*hl= *([0-9]*).*l= *([0-9]*).*", line)
            if match:
                print(f"Extracting cert {certNr} of {certCount}", end="\r")
                certNr += 1
                offset = int(match.group(1))
                header_len = int(match.group(2))
                octet_len = int(match.group(3))

                # Extract PEM certificate
                data = signedData[offset : offset + header_len + octet_len]
                cert, err = execute("openssl x509 -inform der -outform pem", data)
                certs.append(cert)
            else:
                print("Failed match")

    print(f"\nExtracted {len(certs)} certs")
    return certs

def uniqueHash(cert):
    data, err = execute("openssl x509 -hash -fingerprint -inform PEM -noout", cert)
    items = data.decode("utf8").split("\n")
    fingerprint = items[1].strip()
    if fingerprint not in fingerprints:
        fingerprints.append(fingerprint)
        return True

    return False

def execute(cmd, data=None):
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if data is not None:
        res.stdin.write(data)
        res.stdin.close()
    out = res.stdout.read()
    err = res.stderr.read()

    return out, err

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid number of parameters:")
        print("")
        print("Usage - python extract.py [masterlist1.ml|ldif] [masterlist2.ml|ldif]")
        print("")
        exit(1)

    main(sys.argv[1], sys.argv[2])