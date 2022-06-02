
import pyrebase
import streamlit as st
import requests
from datetime import datetime
from PIL import Image
from streamlit_option_menu import option_menu

# Firebase Key
firebaseConfig = {
  'apiKey': "AIzaSyCJwm-xJWxQAzLvoBjvbzaZ6YqhloWunw0",
  'authDomain': "certipros-dc830.firebaseapp.com",
  'databaseURL': "https://certipros-dc830-default-rtdb.firebaseio.com/",
  'projectId': "certipros-dc830",
  'storageBucket': "certipros-dc830.appspot.com",
  'messagingSenderId': "1005129749567",
  'appId': "1:1005129749567:web:63c0bfbc8f9f21a494d48a",
  'measurementId': "G-2QLX72XJ97"
}


  
# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Firebase Database
fb_db = firebase.database()
fb_storage = firebase.storage()

# Set body font size and style
st.markdown(""" <style> .body_font {
font-size:17px ; font-family: 'Courier New'; color: #C6CDD4;} 
#</style> """, unsafe_allow_html=True)

# Set header font size and style
st.markdown(""" <style> .header_font {
font-size:45px ; font-family: 'Courier New'; color: #C6CDD4;} 
#</style> """, unsafe_allow_html=True)

# Set title font size and style
st.markdown(""" <style> .title_font {
font-size:95px ; font-family: 'Courier New'; color: #C6CDD4;} 
#</style> """, unsafe_allow_html=True)


#Main Page
st.markdown('<p class="title_font">CertiPros</p>', unsafe_allow_html=True)

# Create a login and signup selectbox
st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
with st.sidebar:
    viewing_options = option_menu(
    menu_title = None,
    options = ["Login", "Join"],
    menu_icon="cast", default_index=1, orientation="horizontal")
    
# Create a user Input for email and password
email = st.sidebar.text_input('Enter Email')
password = st.sidebar.text_input('Enter Password',type = 'password')


# User signup info
if viewing_options == 'Join':
    name = st.sidebar.text_input('Enter First and Last Name')
    eth_address = st.sidebar.text_input('Enter Ethereum Account Address')
    username = st.sidebar.text_input('Choose a Username', value='Default')
    confirmation = st.sidebar.button('Create my account')

    if confirmation:
        user = auth.create_user_with_email_and_password(email, password)
        st.sidebar.success('Your account was successfully created!')
        st.sidebar.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        fb_db.child(user['localId']).child("Username").set(username)
        fb_db.child(user['localId']).child("ID").set(user['localId'])
        fb_db.child(user['localId']).child("Name").set(name)
        fb_db.child(user['localId']).child("Eth_address").set(eth_address)
        st.title('Welcome ' + username)
        st.info('Login via login drop down selection')

# User login info
if viewing_options == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        name = fb_db.child(user['localId']).child("Name").get().val()
        st.write('<style>div.column-widget.stRadio > div{flex-direction: column;}</style>', unsafe_allow_html=True)
        viewing_options = option_menu(
            menu_title = None,
            options = ["Home", "Community"],
            menu_icon="cast", default_index=1, orientation="horizontal"
        )

        # Home Page
        if viewing_options == 'Home':
            # User name
            st.markdown('<p class="header_font">%s</p>'%name, unsafe_allow_html=True)
            col1, col2 = st.columns([0.7, 0.3])
            # Column for Profile picture

            with col1:
                # Check for profile picture
                image1 = fb_db.child(user['localId']).child("Image").get().val() 
                # Image Found
                if image1 is not None:
                    # Store all images under the child image
                    Image = fb_db.child(user['localId']).child("Image").get()
                    for img in Image.each():
                        img_choice = img.val()
                    st.image(img_choice,use_column_width=True)
                
                    # User plan to change profile picture
                    user_change = st.expander('Change Profile Image')  

                    with user_change:
                        new_image = st.file_uploader("", type=['jpg','png','jpeg'])               
                        upload_new = st.button('Upload')
                        if upload_new:
                            user_id = user['localId']
                            fireb_upload = fb_storage.child(user_id).put(new_image,user['idToken'])
                            imgdata_url = fb_storage.child(user_id).get_url(fireb_upload['downloadTokens']) 
                            fb_db.child(user['localId']).child("Image").push(imgdata_url)
                            st.success('Success!')
                        
                # If there is no images
                else:
                    st.markdown("Add Profile Image")
                    new_image = st.file_uploader("", type=['jpg','png','jpeg'])
                    upload_new = st.button('Upload')

                    if upload_new:
                        user_id = user['localId']
                        # Stored Initated Bucket in Firebase
                        fireb_upload = fb_storage.child(user_id).put(new_image,user['idToken'])
                        # Get the url for easy access
                        a_imgdata_url = fb_storage.child(user_id).get_url(fireb_upload['downloadTokens'])
                        # Put it in our real time database
                        fb_db.child(user['localId']).child("Image").push(a_imgdata_url)


            # This column for the post display
            with col2:
                st.markdown('<p class="body_font">Ethereum Account Address</p>', unsafe_allow_html=True)

                       # Check for Eth Address
                wallet = fb_db.child(user['localId']).child("Eth_address").get().val() 
                # Resume Found
                if wallet is not None:
                     # We plan to store all our image under the child Resume
                    user_wallet = fb_db.child(user['localId']).child("Eth_address").get()
                    wallet_choice = user_wallet.val() 
                    st.write(wallet_choice,use_column_width=True)

                # Dropdown box with users resume and certificates
            select_document = st.selectbox('Select an Option', ['Resume', 'Certificates'])

            if select_document == 'Resume':
                 # Check for resume
                doc = fb_db.child(user['localId']).child("Resume").get().val() 
                # Resume Found
                if doc is not None:
                     # We plan to store all our image under the child Resume
                    user_doc = fb_db.child(user['localId']).child("Resume").get()
                    for doc in user_doc.each():
                        doc_choice = doc.val()
                        if doc_choice:
                            st.image(doc_choice,use_column_width=True)

                else:
                    st.markdown("Add Resume")
                    new_document = st.file_uploader("Resume", type=['jpg','png','jpeg'])
                    file_upload = st.button("Upload Document")

                    if file_upload:
                        user_id = user['localId']
                        firebase_upload = fb_storage.child(user_id).put(new_document,user['idToken'])
                        doc_data_url = fb_storage.child(user_id).get_url(firebase_upload['downloadTokens']) 
                        fb_db.child(user['localId']).child("Resume").push(doc_data_url)
                        st.success('Success!')

            if select_document == 'Certificates':
                # Function to render assets
                def render_asset(asset):
                    if asset['image_url']:
                        st.image(asset['image_url'])
                ## Opensea call
                params = {'owner': wallet_choice,
                          'limit': 1
                          }
                r = requests.get("https://testnets-api.opensea.io/api/v1/assets", params=params)
                assets = r.json()['assets']
                for asset in assets:                
                    asset = render_asset(asset)
                        
           # Community Page
        if viewing_options == 'Community':
            all_users = fb_db.get()
            res = []
            # Store all the users handle name
            for name in all_users.each():
                print(name.val())
                try:
                    k = name.val()["Name"]
                    res.append(k)
                except:
                    pass
                
            # Total users
            nl = len(res)
            st.write('Total users here: '+ str(nl)) 
            
             # Allow the user to choose which other user he/she wants to see 
            choice = st.selectbox('My Collegues',res)
            if 'push' not in st.session_state:
                st.session_state.push = False
            push = st.checkbox('Show Profile')
            
            # Show the choosen Profile
            if push:
                for name in all_users.each():
                    try:
                        k = name.val()["Name"]
                    except:
                        pass
                    # 
                    if k == choice:
                        try:
                            lid = name.val()["ID"]
                            user_name = fb_db.child(lid).child("Name").get().val()             
                            st.markdown(user_name, unsafe_allow_html=True)
                              # User name
                            st.markdown('<p class="header_font">%s</p>'%name, unsafe_allow_html=True)
                            col1, col2 = st.columns([0.7, 0.3])
                            # Column for Profile picture
                            with col1:
                                # Check for profile picture
                                image1 = fb_db.child(user['localId']).child("Image").get().val() 
                                # Image Found
                                if image1 is not None:
                                    # We plan to store all our image under the child image
                                    Image = fb_db.child(user['localId']).child("Image").get()
                                    for img in Image.each():
                                        img_choice = img.val()
                                        st.image(img_choice,use_column_width=True)

                            with col2:
                                st.markdown('<p class="body_font">Ethereum Account Address</p>', unsafe_allow_html=True)
                                # Check for Eth Address
                                wallet = fb_db.child(user['localId']).child("Eth_address").get().val() 
                                # Resume Found
                                if wallet is not None:
                                    # We plan to store all our image under the child Resume
                                    user_wallet = fb_db.child(user['localId']).child("Eth_address").get()
                                    wallet_choice = user_wallet.val() 
                                    st.write(wallet_choice,use_column_width=True)

                            select_options = ['Resume', 'Certificates']
                            page = st.radio('Select an Option', select_options)
                            #select_document = st.checkbox('Select an Option', ['Resume', 'Certificates'])

                            if page == 'Resume':

                                 # Check for resume              
                                doc = fb_db.child(user['localId']).child("Resume").get().val() 
                                # Resume Found
                            if doc is not None:
                                # We plan to store all our image under the child Resume
                                user_doc = fb_db.child(user['localId']).child("Resume").get()
                                for doc in user_doc.each():
                                    doc_choice = doc.val()
                                    if doc_choice:
                                        st.image(doc_choice,use_column_width=True)

                            if page == 'Certificates':

                            # Function to render assets
                                def render_asset(asset):
                                    if asset['image_url']:
                                        st.image(asset['image_url'])
                            ## Opensea call
                                params = {'owner': wallet_choice,
                                          'limit': 1
                                          }
                                r = requests.get("https://testnets-api.opensea.io/api/v1/assets", params=params)
                                assets = r.json()['assets']
                                for asset in assets:                
                                    render_asset(asset)

                        except:
                            pass
