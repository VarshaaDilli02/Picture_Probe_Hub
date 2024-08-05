# importing necessary libraries
from flask import Flask, render_template, request
from serpapi import GoogleSearch
import pandas as pd
import requests
import os
import cv2
import numpy as np
import pywt
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function to upload image to IMGBB
def upload_image_to_imgbb(image_path, api_key):
    url = "https://api.imgbb.com/1/upload"
    files = {"image": (image_path, open(image_path, "rb"))}
    params = {"key": api_key}
        
    response = requests.post(url, files=files, params=params)
    data = response.json()
    
    return data.get("data", {}).get("url")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file:
                image_filename = file.filename
                image_path = os.path.join(image_folder, image_filename)
                file.save(image_path)
                
                action = request.form.get('action')  # Get the value of the action button clicked
                
                if action == 'search':  # Perform search operation
                    api_key = "c5534ab496d66ea7b8f0a1991b10b076"
                    url = upload_image_to_imgbb(image_path, api_key)     
                    
                    if url:
                        params = {
                            "engine": "google_lens",
                            "url": url,
                            "no_cache": "true",
                            "api_key": "f3efab1714ff1f2ce0a494a24d98f84c7746fc241494d995d9183dbd32125445",
                        }

                        search = GoogleSearch(params)
                        results = search.get_dict()

                        name_url_thumbnail = []

                        if results['search_metadata']['status'] != "Success":
                            print("no item found")
                        else:
                            for item in results['visual_matches']:
                                name_url_thumbnail.append({
                                    "source": item.get('source'),
                                    "title": item.get('title'),
                                    "link": item.get('link'),
                                    "thumbnail": item.get('thumbnail')
                                })

                        df = pd.DataFrame(name_url_thumbnail)
                        filtered_df = df[df['link'].notnull()]
                        filtered_df = filtered_df.reset_index()
                        filtered_df = filtered_df[["source","link"]]

                        filtered_df.to_csv("results.csv", index=False)

                        return render_template('url_finder.html', data=filtered_df.to_dict('records'), image=image_filename)
                    else:
                        return "Error uploading image... retry again :)"

        except Exception as e:
            return f"Error: {e}"

    return render_template('index.html', data=[])

image_folder = "uploads"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Main call
if __name__ == '__main__':
    app.run(debug=True)