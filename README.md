# Profile Pictures Editor  

## Overview  
Profile Pictures Editor is a tool designed for easy and efficient cropping of employee profile photos. It allows users to drag and drop images, select dimensions, and automatically detect faces for accurate cropping.  

## Features  
- **Drag and Drop Upload** – Upload images via drag-and-drop or file selection.  
- **Batch Processing** – Add multiple images at once.  
- **Custom Dimensions** – Select the required photo size.  
- **Progress Bar** – Provides real-time updates on the processing status.  
- **Automated Face Detection** – Uses OpenCV’s Haar Cascade for accurate cropping.  
- **Download Processed Images** – Outputs a ZIP file with cropped images.  
- **Error Handling** – Uncroppable images are moved to an "unacceptable" folder with details in a log file.  

## Output Structure  
- **Accepted Images** – Properly cropped images are stored in the output folder.  
- **Unacceptable Images** – Images that couldn't be cropped properly are placed in the "unacceptable" folder with a log (`1.unacceptable.txt`).  

## How It Works  
1. **Upload Images** – Drag and drop or select multiple photos.  
2. **Choose Dimensions** – Select the required size for the profile photos.  
3. **Face Detection & Cropping** – The system detects faces and adjusts the crop to include hair and shoulders.  
4. **Progress Bar Updates** – Track the status of image processing.  
5. **Download Results** – Get a ZIP file containing all the cropped images.  

## Tech Stack  
- **Backend:** Flask (Python)  
- **Frontend:** HTML, JavaScript  
- **Image Processing:** OpenCV (Haar Cascade)  

## Security Considerations  
Since this application processes confidential employee images, it's designed for **local use only**. To ensure privacy, all uploaded files are cleared from the system once processing is complete.  

## EXE Application Download
https://github.com/22023942-JinYi/Profile-Pictures/releases/download/ProfilePicturesEditor/ProfilePicturesEdit.exe
