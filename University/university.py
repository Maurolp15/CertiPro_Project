import os
import json
from web3.auto import Web3, w3
from web3 import IPCProvider 
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import datetime
import webbrowser

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json


#Read a private key from an environment variable
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

# connect to the IPC location started with 'geth --dev --datadir ~/mynode'
#w3 = Web3(IPCProvider('~/mynode/geth.ipc'))
from web3.middleware import geth_poa_middleware

# Make connection to blockchain
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
# inject the poa compatibility middleware to the innermost layer
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# confirm that the connection succeeded
w3.clientVersion
'Geth/v1.7.3-stable-4bb3c89d/linux-amd64/go1.9'


grn = os.environ.get("GRN")

account: LocalAccount = Account.from_key(grn)
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

# Load environmental variables
load_dotenv("SAMPLE.env")


def load_contract():
    
    with open(Path("./contracts/compiled/certificate_abi.json")) as file:
        abi = json.load(file)
        
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    return contract
    
    
cert_contract = load_contract()

##### ADD FILES TO IPFS #####

def pin_cert(cert_name, cert_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(cert_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": cert_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash


def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash
    

################################################################################
# Award Certificate
################################################################################

account = os.getenv("ACCOUNT")
contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
cert_name = st.text_input("Certificate Name: ")
student_account=st.text_input("Enter the student address")
certificate_details = st.text_input("Certificate Details", value="Miami FinTech Certificate of Completion")

file = st.file_uploader("Upload Certificate", type=["jpg", "jpeg", "png", "pdf"])

if st.button("Award Certificate"):
    cert_ipfs_hash = pin_cert(cert_name, file)
    cert_uri = f"ipfs://{cert_ipfs_hash}"
    tx_hash = cert_contract.functions.awardCertificate(
        student_account,
        cert_uri
    ).transact({'from': account, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Certificate IPFS Gateway Link](https://ipfs.io/ipfs/{cert_ipfs_hash})")

    file = str(file)
    filename = file.split("\'")
    pic = filename[1]
    with open(Path(f"./{pic}"), 'r'):
         os.system(f"lpr -P Canon_MG2500_series -o orientation-requested=4 {pic}")

    now = datetime.datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
 
    file = open('read.txt', 'w')
    file.write(f"______________{date_time}\n")
    file.write(f"______________https://ipfs.io/ipfs/{cert_ipfs_hash}")
    file.close()
    os.system("lpr -P Canon_MG2500_series -o orientation-requested=4 read.txt")

qrcode_file = st.file_uploader("Upload QR Code", type=["jpg", "jpeg", "png", "pdf"])

if st.button("Print QR Code"):
    qrcode = str(qrcode_file)
    qrcode = qrcode.split("\'")
    qr = qrcode[1]
    with open(Path(f"./{qr}"), 'r'):
         os.system(f"lpr -P Canon_MG2500_series -o orientation-requested=4 {qr}")


st.markdown("---")
    

################################################################################
# Display Certificate
################################################################################

#certificate_image = (f"https://ipfs.io/ipfs/{cert_ipfs_hash}")

certificate_id = st.number_input("Enter a Certificate Token ID to display", value=0, step=1)
if st.button("Display Certificate"):
    # Get the certificate owner
    certificate_owner = cert_contract.functions.ownerOf(certificate_id).call()
    st.write(f"The certificate was awarded to {certificate_owner}")

    # Get the certificate's metadata
    certificate_uri = cert_contract.functions.tokenURI(certificate_id).call()
    st.write(f"The certificate's tokenURI metadata is {certificate_uri}") 

    st.image(f"https://ipfs.io/ipfs/{certificate_uri}")
    
   

#if st.button("Display image ipfs hash"): 
   #url = "https://www..com" 
   #webbrowser.open(certificate_uri)